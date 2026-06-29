"""Retrieval-specific helpers built on the local data-task-scorers core."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from statistics import fmean
from typing import Any, TypeAlias

import pandas as pd

from .eval_core import EvalItem, Scorer, ScorerContext, create_scorer, run_eval


@dataclass(frozen=True, slots=True)
class RetrievedDocument:
    """One result returned by any first- or second-stage retriever.

    ``evidence_ids`` make parent-child comparisons fair. A child chunk and its
    returned parent page can both point at the same canonical source evidence.
    """

    id: str
    text: str
    score: float | None = None
    evidence_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def canonical_evidence_ids(self) -> tuple[str, ...]:
        return self.evidence_ids or (self.id,)


@dataclass(frozen=True, slots=True)
class EvalCase:
    """A reviewed question and the source evidence that should be retrieved."""

    id: str
    query: str
    relevant_evidence_ids: tuple[str, ...]
    tags: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Every evaluation case needs a stable id.")
        if not self.query.strip():
            raise ValueError(f"Evaluation case {self.id!r} needs a query.")
        if not self.relevant_evidence_ids:
            raise ValueError(
                f"Evaluation case {self.id!r} needs at least one relevant evidence id."
            )


@dataclass(frozen=True, slots=True)
class RetrievalMetrics:
    hit_at_k: float
    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float


@dataclass(frozen=True, slots=True)
class EvalRow:
    case: EvalCase
    documents: tuple[RetrievedDocument, ...]
    metrics: RetrievalMetrics
    latency_ms: float


@dataclass(frozen=True, slots=True)
class EvalReport:
    name: str
    k: int
    rows: tuple[EvalRow, ...]

    def summary(self) -> dict[str, float | int | str]:
        """Return simple mean metrics suitable for a comparison table."""
        if not self.rows:
            raise ValueError("Cannot summarize an empty evaluation report.")
        return {
            "retriever": self.name,
            "k": self.k,
            "cases": len(self.rows),
            "hit_rate": fmean(row.metrics.hit_at_k for row in self.rows),
            "precision_at_k": fmean(row.metrics.precision_at_k for row in self.rows),
            "recall_at_k": fmean(row.metrics.recall_at_k for row in self.rows),
            "mrr": fmean(row.metrics.reciprocal_rank for row in self.rows),
            "mean_latency_ms": fmean(row.latency_ms for row in self.rows),
        }

    def case_table(self) -> pd.DataFrame:
        """Return inspectable per-case evidence and metrics."""
        return pd.DataFrame(
            [
                {
                    "case_id": row.case.id,
                    "query": row.case.query,
                    "tags": ", ".join(row.case.tags),
                    "retrieved_ids": [document.id for document in row.documents],
                    "hit@k": row.metrics.hit_at_k,
                    "precision@k": row.metrics.precision_at_k,
                    "recall@k": row.metrics.recall_at_k,
                    "reciprocal_rank": row.metrics.reciprocal_rank,
                    "latency_ms": row.latency_ms,
                }
                for row in self.rows
            ]
        )


Retriever: TypeAlias = Callable[[str, int], Sequence[RetrievedDocument]]


def _deduplicate(documents: Sequence[RetrievedDocument]) -> tuple[RetrievedDocument, ...]:
    """Preserve rank while dropping repeated document IDs."""
    seen: set[str] = set()
    unique: list[RetrievedDocument] = []
    for document in documents:
        if document.id not in seen:
            unique.append(document)
            seen.add(document.id)
    return tuple(unique)


def _score_case(case: EvalCase, documents: Sequence[RetrievedDocument]) -> RetrievalMetrics:
    relevant = set(case.relevant_evidence_ids)
    relevant_result_count = 0
    found_evidence: set[str] = set()
    first_relevant_rank: int | None = None

    for rank, document in enumerate(documents, start=1):
        document_evidence = set(document.canonical_evidence_ids)
        matched_evidence = relevant & document_evidence
        if matched_evidence:
            relevant_result_count += 1
            found_evidence.update(matched_evidence)
            if first_relevant_rank is None:
                first_relevant_rank = rank

    document_count = len(documents)
    return RetrievalMetrics(
        hit_at_k=float(first_relevant_rank is not None),
        precision_at_k=(relevant_result_count / document_count) if document_count else 0.0,
        recall_at_k=len(found_evidence) / len(relevant),
        reciprocal_rank=(1 / first_relevant_rank) if first_relevant_rank else 0.0,
    )


def retrieval_scorers() -> tuple[Scorer, ...]:
    """Return the reusable retrieval scorers used by the convenience wrapper."""

    def metric_scorer(
        name: str,
        description: str,
        attribute: str,
    ) -> Scorer:
        def score(context: ScorerContext) -> float:
            if not isinstance(context.expected, EvalCase):
                raise TypeError("Retrieval scorers require EvalCase expected values.")
            documents = tuple(context.output)
            metrics = _score_case(context.expected, documents)
            return float(getattr(metrics, attribute))

        return create_scorer(name=name, description=description, scorer=score)

    return (
        metric_scorer(
            "hit_rate",
            "Whether any reviewed evidence appeared in the retrieved results.",
            "hit_at_k",
        ),
        metric_scorer(
            "precision_at_k",
            "Share of retrieved results that match reviewed evidence.",
            "precision_at_k",
        ),
        metric_scorer(
            "recall_at_k",
            "Share of reviewed evidence recovered by the retrieved results.",
            "recall_at_k",
        ),
        metric_scorer(
            "mrr",
            "Reciprocal rank of the first retrieved relevant result.",
            "reciprocal_rank",
        ),
    )


def run_retrieval_eval(
    name: str,
    cases: Sequence[EvalCase],
    retriever: Retriever,
    *,
    k: int = 5,
) -> EvalReport:
    """Run one retriever against reviewed cases and retain every ranked result."""
    if k < 1:
        raise ValueError("k must be at least 1")

    data = tuple(
        EvalItem(
            id=case.id,
            input=case.query,
            expected=case,
            tags=case.tags,
            metadata={"notes": case.notes},
        )
        for case in cases
    )

    def task(query: str) -> tuple[RetrievedDocument, ...]:
        return _deduplicate(tuple(retriever(query, k)))[:k]

    generic_report = run_eval(
        name,
        data=data,
        task=task,
        scorers=retrieval_scorers(),
    )
    rows: list[EvalRow] = []
    for generic_row in generic_report.rows:
        case = generic_row.item.expected
        if not isinstance(case, EvalCase):
            raise TypeError("Retrieval evaluation data must carry EvalCase expected values.")
        documents = tuple(generic_row.output)
        rows.append(
            EvalRow(
                case=case,
                documents=documents,
                metrics=RetrievalMetrics(
                    hit_at_k=generic_row.score("hit_rate").score,
                    precision_at_k=generic_row.score("precision_at_k").score,
                    recall_at_k=generic_row.score("recall_at_k").score,
                    reciprocal_rank=generic_row.score("mrr").score,
                ),
                latency_ms=generic_row.task_latency_ms,
            )
        )
    return EvalReport(name=name, k=k, rows=tuple(rows))


def compare_reports(*reports: EvalReport) -> pd.DataFrame:
    """Compare reports that used the same cases and retrieval depth.

    The function deliberately refuses apples-to-oranges summaries. A chart is
    only useful when its candidates saw the same questions and the same ``k``.
    """
    if len(reports) < 2:
        raise ValueError("Compare at least two reports.")

    reference_case_ids = tuple(row.case.id for row in reports[0].rows)
    reference_k = reports[0].k
    for report in reports[1:]:
        if report.k != reference_k:
            raise ValueError("All compared reports must use the same k.")
        if tuple(row.case.id for row in report.rows) != reference_case_ids:
            raise ValueError("All compared reports must use the same ordered cases.")

    table = pd.DataFrame(report.summary() for report in reports)
    return table.sort_values(
        ["recall_at_k", "mrr", "mean_latency_ms"],
        ascending=[False, False, True],
        ignore_index=True,
    )
