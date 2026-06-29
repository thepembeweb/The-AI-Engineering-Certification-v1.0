"""Answer-level RAG scorers for the local Evalite-shaped evaluation core."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import sqrt
from statistics import fmean
from typing import Any, Protocol

from pydantic import BaseModel, Field

from .eval_core import Score, Scorer, ScorerContext, create_scorer
from .retrieval_eval import RetrievedDocument


@dataclass(frozen=True, slots=True)
class AnswerOutput:
    """The answer and the retrieved passages that were given to the answer model."""

    answer: str
    documents: tuple[RetrievedDocument, ...]

    @property
    def ground_truth(self) -> tuple[str, ...]:
        """Return non-empty retrieved passages for the faithfulness scorer."""
        return tuple(document.text for document in self.documents if document.text.strip())


@dataclass(frozen=True, slots=True)
class StatementVerdict:
    """One answer claim and the judge's support decision."""

    statement: str
    reason: str
    verdict: int

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("A faithfulness verdict needs a statement.")
        if not self.reason.strip():
            raise ValueError("A faithfulness verdict needs a reason.")
        if self.verdict not in {0, 1}:
            raise ValueError("A faithfulness verdict must be 0 or 1.")


@dataclass(frozen=True, slots=True)
class FaithfulnessResult:
    """The fraction of judged answer claims supported by retrieved passages."""

    score: float
    verdicts: tuple[StatementVerdict, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Faithfulness must be between 0 and 1.")

    @property
    def unsupported_statements(self) -> tuple[str, ...]:
        return tuple(verdict.statement for verdict in self.verdicts if verdict.verdict == 0)


@dataclass(frozen=True, slots=True)
class AnswerSimilarityResult:
    """Embedding cosine similarity between a generated and reference answer."""

    score: float
    raw_cosine_similarity: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Answer similarity must be between 0 and 1.")


class EmbeddingModel(Protocol):
    """The small part of an embeddings client needed by answer similarity."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...


class FaithfulnessJudge(Protocol):
    """A judge that marks each factual answer statement as supported or not."""

    def __call__(
        self,
        *,
        question: str,
        answer: str,
        ground_truth: Sequence[str],
    ) -> Sequence[StatementVerdict]: ...


class _JudgedStatement(BaseModel):
    statement: str = Field(description="One factual statement from the answer.")
    reason: str = Field(
        description="Why the supplied ground-truth passages do or do not support it."
    )
    verdict: int = Field(
        description="Use 1 when the passages support the statement; otherwise use 0.",
        ge=0,
        le=1,
    )


class _FaithfulnessAssessment(BaseModel):
    statements: list[_JudgedStatement] = Field(default_factory=list)


_FAITHFULNESS_INSTRUCTIONS = (
    "You are grading faithfulness in a retrieval-augmented answer.\n\n"
    "Break the answer into independently checkable factual statements. For each "
    "statement, use only the supplied ground-truth passages. Give verdict 1 when "
    "one or more passages support the statement directly or by an unambiguous "
    "paraphrase. Give verdict 0 when support is missing, incomplete, or "
    "contradicted. Do not use outside knowledge. If the answer has no factual "
    "claims, return an empty statements list."
)


def _field(value: Any, name: str) -> Any:
    if isinstance(value, Mapping):
        return value[name]
    return getattr(value, name)


def make_openai_faithfulness_judge(model: Any) -> FaithfulnessJudge:
    """Create a claim-level faithfulness judge from a LangChain chat model."""

    structured_model = model.with_structured_output(_FaithfulnessAssessment)

    def judge(
        *,
        question: str,
        answer: str,
        ground_truth: Sequence[str],
    ) -> tuple[StatementVerdict, ...]:
        sources = "\n\n".join(
            f"[Source {index}]\n{passage}"
            for index, passage in enumerate(ground_truth, start=1)
        )
        assessment = structured_model.invoke(
            [
                ("system", _FAITHFULNESS_INSTRUCTIONS),
                (
                    "human",
                    f"Question:\n{question}\n\n"
                    f"Ground truth passages:\n{sources}\n\n"
                    f"Answer:\n{answer}",
                ),
            ]
        )
        statements = _field(assessment, "statements")
        return tuple(
            StatementVerdict(
                statement=str(_field(statement, "statement")),
                reason=str(_field(statement, "reason")),
                verdict=int(_field(statement, "verdict")),
            )
            for statement in statements
        )

    return judge


def faithfulness(
    *,
    question: str,
    answer: str,
    ground_truth: Sequence[str],
    judge: FaithfulnessJudge,
) -> FaithfulnessResult:
    """Score the percentage of factual answer claims supported by the context."""

    passages = tuple(passage.strip() for passage in ground_truth if passage.strip())
    if not answer.strip() or not passages:
        return FaithfulnessResult(score=0.0, verdicts=())

    verdicts = tuple(judge(question=question, answer=answer, ground_truth=passages))
    if not verdicts:
        return FaithfulnessResult(score=1.0, verdicts=())
    return FaithfulnessResult(
        score=fmean(verdict.verdict for verdict in verdicts),
        verdicts=verdicts,
    )


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding vectors must have the same dimension.")
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        raise ValueError("Embedding vectors must not be all zero.")
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


def answer_similarity(
    *,
    answer: str,
    reference: str,
    embedding_model: EmbeddingModel,
) -> AnswerSimilarityResult:
    """Compare answer meaning with a reviewed reference using cosine similarity."""

    if not answer.strip() or not reference.strip():
        return AnswerSimilarityResult(score=0.0, raw_cosine_similarity=0.0)

    embeddings = embedding_model.embed_documents([answer, reference])
    if len(embeddings) != 2:
        raise ValueError("The embedding model must return one vector per input text.")
    raw_cosine = _cosine_similarity(embeddings[0], embeddings[1])
    return AnswerSimilarityResult(
        score=max(0.0, min(1.0, raw_cosine)),
        raw_cosine_similarity=raw_cosine,
    )


def _answer_output(context: ScorerContext) -> AnswerOutput:
    if not isinstance(context.output, AnswerOutput):
        raise TypeError("Answer-level scorers require the task to return AnswerOutput.")
    return context.output


def faithfulness_scorer(judge: FaithfulnessJudge) -> Scorer:
    """Create a reusable scorer that audits answer claims against retrieved text."""

    def score(context: ScorerContext) -> Score:
        output = _answer_output(context)
        result = faithfulness(
            question=str(context.input),
            answer=output.answer,
            ground_truth=output.ground_truth,
            judge=judge,
        )
        return Score(
            score=result.score,
            metadata={
                "verdicts": [
                    {
                        "statement": verdict.statement,
                        "reason": verdict.reason,
                        "verdict": verdict.verdict,
                    }
                    for verdict in result.verdicts
                ],
                "unsupported_statements": list(result.unsupported_statements),
            },
        )

    return create_scorer(
        name="faithfulness",
        description="Share of answer claims supported by the retrieved passages.",
        scorer=score,
    )


def answer_similarity_scorer(embedding_model: EmbeddingModel) -> Scorer:
    """Create a reusable scorer that compares an answer with its reference."""

    def score(context: ScorerContext) -> Score:
        output = _answer_output(context)
        result = answer_similarity(
            answer=output.answer,
            reference=str(context.expected),
            embedding_model=embedding_model,
        )
        return Score(
            score=result.score,
            metadata={"raw_cosine_similarity": result.raw_cosine_similarity},
        )

    return create_scorer(
        name="answer_similarity",
        description="Embedding cosine similarity between output and reference answer.",
        scorer=score,
    )

