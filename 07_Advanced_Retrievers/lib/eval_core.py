"""A small Evalite-shaped core for local, synchronous evaluations.

The public shape is deliberately simple:

    run_eval(name, data=..., task=..., scorers=[...])

Each scorer receives an item's input, the task output, and its expected value.
It returns a score from 0 to 1 plus optional inspectable metadata.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from statistics import fmean
from time import perf_counter
from typing import Any, TypeAlias

import pandas as pd


@dataclass(frozen=True, slots=True)
class EvalItem:
    """One reviewed input and expected value for a generic evaluation run."""

    id: str
    input: Any
    expected: Any
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Every evaluation item needs a stable id.")


@dataclass(frozen=True, slots=True)
class Score:
    """A normalized scorer result and optional details for later inspection."""

    score: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("A scorer result must be between 0 and 1.")


@dataclass(frozen=True, slots=True)
class ScorerContext:
    """The values available to every scorer, matching Evalite's core shape."""

    item: EvalItem
    output: Any

    @property
    def input(self) -> Any:
        return self.item.input

    @property
    def expected(self) -> Any:
        return self.item.expected


ScorerFunction: TypeAlias = Callable[[ScorerContext], Score | float]


@dataclass(frozen=True, slots=True)
class Scorer:
    """A reusable named scorer for an evaluation run."""

    name: str
    description: str
    scorer: ScorerFunction

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("A scorer needs a name.")
        if not self.description.strip():
            raise ValueError(f"Scorer {self.name!r} needs a description.")

    def evaluate(self, context: ScorerContext) -> Score:
        result = self.scorer(context)
        if isinstance(result, Score):
            return result
        if isinstance(result, (int, float)):
            return Score(score=float(result))
        raise TypeError(
            f"Scorer {self.name!r} must return Score or a number between 0 and 1."
        )


def create_scorer(
    name: str,
    description: str,
    scorer: ScorerFunction,
) -> Scorer:
    """Create a named scorer, mirroring Evalite's reusable scorer pattern."""

    return Scorer(name=name, description=description, scorer=scorer)


Task: TypeAlias = Callable[[Any], Any]


@dataclass(frozen=True, slots=True)
class EvalRunRow:
    item: EvalItem
    output: Any
    scores: Mapping[str, Score]
    task_latency_ms: float
    scoring_latency_ms: float

    def score(self, scorer_name: str) -> Score:
        try:
            return self.scores[scorer_name]
        except KeyError as error:
            raise KeyError(f"No score named {scorer_name!r} in this evaluation row.") from error


@dataclass(frozen=True, slots=True)
class EvalRunReport:
    name: str
    scorers: tuple[Scorer, ...]
    rows: tuple[EvalRunRow, ...]

    def summary(self) -> dict[str, float | int | str]:
        """Return mean scores and latency for a compact comparison table."""

        if not self.rows:
            raise ValueError("Cannot summarize an empty evaluation report.")
        return {
            "evaluation": self.name,
            "cases": len(self.rows),
            **{
                scorer.name: fmean(row.score(scorer.name).score for row in self.rows)
                for scorer in self.scorers
            },
            "mean_task_latency_ms": fmean(row.task_latency_ms for row in self.rows),
            "mean_scoring_latency_ms": fmean(
                row.scoring_latency_ms for row in self.rows
            ),
        }

    def case_table(self) -> pd.DataFrame:
        """Return inputs, outputs, scores, and scorer metadata for each item."""

        rows: list[dict[str, Any]] = []
        for row in self.rows:
            table_row: dict[str, Any] = {
                "case_id": row.item.id,
                "input": row.item.input,
                "expected": row.item.expected,
                "tags": ", ".join(row.item.tags),
                "output": row.output,
                "task_latency_ms": row.task_latency_ms,
                "scoring_latency_ms": row.scoring_latency_ms,
            }
            for scorer in self.scorers:
                result = row.score(scorer.name)
                table_row[scorer.name] = result.score
                table_row[f"{scorer.name}_metadata"] = dict(result.metadata)
            rows.append(table_row)
        return pd.DataFrame(rows)


def run_eval(
    name: str,
    *,
    data: Sequence[EvalItem],
    task: Task,
    scorers: Sequence[Scorer],
) -> EvalRunReport:
    """Run data through a task, then score every output with every scorer."""

    if not name.strip():
        raise ValueError("An evaluation needs a name.")
    if not data:
        raise ValueError("An evaluation needs at least one data item.")
    if not scorers:
        raise ValueError("An evaluation needs at least one scorer.")

    scorer_names = [scorer.name for scorer in scorers]
    if len(set(scorer_names)) != len(scorer_names):
        raise ValueError("Each scorer in an evaluation needs a unique name.")

    rows: list[EvalRunRow] = []
    for item in data:
        task_started = perf_counter()
        output = task(item.input)
        task_latency_ms = (perf_counter() - task_started) * 1_000

        scoring_started = perf_counter()
        context = ScorerContext(item=item, output=output)
        scores = {scorer.name: scorer.evaluate(context) for scorer in scorers}
        scoring_latency_ms = (perf_counter() - scoring_started) * 1_000
        rows.append(
            EvalRunRow(
                item=item,
                output=output,
                scores=scores,
                task_latency_ms=task_latency_ms,
                scoring_latency_ms=scoring_latency_ms,
            )
        )
    return EvalRunReport(name=name, scorers=tuple(scorers), rows=tuple(rows))


def compare_eval_reports(*reports: EvalRunReport) -> pd.DataFrame:
    """Compare generic evaluation runs with the same data and scorers."""

    if len(reports) < 2:
        raise ValueError("Compare at least two evaluation reports.")

    reference_case_ids = tuple(row.item.id for row in reports[0].rows)
    reference_scorers = tuple(scorer.name for scorer in reports[0].scorers)
    for report in reports[1:]:
        if tuple(row.item.id for row in report.rows) != reference_case_ids:
            raise ValueError("All compared reports must use the same ordered data.")
        if tuple(scorer.name for scorer in report.scorers) != reference_scorers:
            raise ValueError("All compared reports must use the same ordered scorers.")

    table = pd.DataFrame(report.summary() for report in reports)
    return table.sort_values(
        [*reference_scorers, "mean_task_latency_ms"],
        ascending=[False] * len(reference_scorers) + [True],
        ignore_index=True,
    )

