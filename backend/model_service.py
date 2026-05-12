from __future__ import annotations

import os
from threading import Lock
from typing import Any, Optional


LABEL_ALIASES = {
    "identity_hate": "Identity-Based Hate",
    "identity_attack": "Identity Attack",
    "insult": "Insult",
    "not_toxic": "Not Toxic",
    "non_toxic": "Not Toxic",
    "obscene": "Obscene Language",
    "severe_toxic": "Severe Toxicity",
    "threat": "Threat",
    "toxic": "Toxicity",
    "toxique": "Toxicity",
}

POSITIVE_CANONICAL_LABELS = {
    "identity_attack",
    "identity_hate",
    "insult",
    "obscene",
    "severe_toxic",
    "threat",
    "toxic",
    "toxicity",
    "toxic_language",
    "offensive",
    "hate",
    "abusive",
}

NEGATIVE_CANONICAL_LABELS = {
    "neutral",
    "not_toxic",
    "non_toxic",
    "safe",
    "clean",
    "non_offensive",
}


class ToxicityModelService:
    def __init__(self) -> None:
        self.model_name = os.getenv("TOXICITY_MODEL_NAME", "unitary/toxic-bert")
        self.threshold = float(os.getenv("TOXICITY_THRESHOLD", "0.50"))
        self._classifier: Optional[Any] = None
        self._load_lock = Lock()
        self._last_error: Optional[str] = None

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    @property
    def is_loaded(self) -> bool:
        return self._classifier is not None

    def ensure_loaded(self) -> None:
        if self._classifier is not None:
            return

        with self._load_lock:
            if self._classifier is not None:
                return

            try:
                from transformers import pipeline
            except Exception as exc:  # pragma: no cover
                self._last_error = str(exc)
                raise RuntimeError(
                    "The ML backend dependencies are not available. Run ./backend.sh to install them."
                ) from exc

            try:
                self._classifier = pipeline(
                    task="text-classification",
                    device=-1,
                    model=self.model_name,
                    top_k=None,
                )
                self._last_error = None
            except Exception as exc:  # pragma: no cover
                self._last_error = str(exc)
                raise RuntimeError(
                    f'Unable to load the local model "{self.model_name}". '
                    "Check your internet connection for the first model download and try again."
                ) from exc

    def analyze(self, comment: str) -> dict[str, Any]:
        normalized_comment = " ".join(comment.split()).strip()
        if not normalized_comment:
            raise ValueError("Comment text is required.")

        self.ensure_loaded()
        raw_prediction = self._classifier(normalized_comment, truncation=True, max_length=512)
        scores = self._normalize_predictions(raw_prediction)

        if not scores:
            raise RuntimeError("The model returned no predictions.")

        top_score = scores[0]["score"]
        toxic_score = self._resolve_toxic_score(scores)
        is_toxic = toxic_score >= self.threshold
        confidence = round((toxic_score if is_toxic else 1 - toxic_score) * 100)
        score = round(toxic_score * 100)

        strong_signal_floor = max(0.10, self.threshold * 0.3)
        positive_scores = [entry for entry in scores if self._is_positive_label(entry["canonicalLabel"])]
        prominent_scores = [entry for entry in positive_scores if entry["score"] >= strong_signal_floor]

        if is_toxic and prominent_scores:
            signal_labels = [entry["displayLabel"] for entry in prominent_scores[:4]]
            primary_signal = signal_labels[0]
            display_categories = prominent_scores
        elif is_toxic and positive_scores:
            signal_labels = [positive_scores[0]["displayLabel"]]
            primary_signal = signal_labels[0]
            display_categories = [positive_scores[0]]
        else:
            signal_labels = ["Neutral Tone"]
            primary_signal = "Neutral Tone"
            display_categories = [
                {
                    "displayLabel": "Neutral Tone",
                    "rawLabel": "neutral",
                    "canonicalLabel": "neutral",
                    "score": max(0.0, 1 - toxic_score),
                }
            ]

        return {
            "comment": normalized_comment,
            "confidence": confidence,
            "isToxic": is_toxic,
            "model": self.model_name,
            "primarySignal": primary_signal,
            "recommendation": self._build_recommendation(is_toxic, toxic_score),
            "score": score,
            "signals": signal_labels,
            "summary": self._build_summary(is_toxic, primary_signal, toxic_score),
            "threshold": round(self.threshold * 100),
            "verdict": "Toxic" if is_toxic else "Not Toxic",
            "categories": [
                {
                    "label": entry["displayLabel"],
                    "rawLabel": entry["rawLabel"],
                    "score": round(entry["score"] * 100),
                }
                for entry in display_categories
            ],
        }

    def metadata(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "model": self.model_name,
            "modelLoaded": self.is_loaded,
            "threshold": round(self.threshold * 100),
            "lastError": self._last_error,
        }

    def _normalize_predictions(self, raw_prediction: Any) -> list[dict[str, Any]]:
        if isinstance(raw_prediction, list) and raw_prediction and isinstance(raw_prediction[0], list):
            entries = raw_prediction[0]
        elif isinstance(raw_prediction, list):
            entries = raw_prediction
        elif isinstance(raw_prediction, dict):
            entries = [raw_prediction]
        else:
            entries = []

        normalized = []
        for entry in entries:
            raw_label = str(entry.get("label", "")).strip()
            canonical_label = self._canonical_label(raw_label)
            normalized.append(
                {
                    "displayLabel": self._pretty_label(raw_label),
                    "rawLabel": raw_label,
                    "canonicalLabel": canonical_label,
                    "score": float(entry.get("score", 0.0)),
                }
            )

        normalized.sort(key=lambda item: item["score"], reverse=True)
        return normalized

    def _pretty_label(self, raw_label: str) -> str:
        canonical = self._canonical_label(raw_label)
        if canonical in LABEL_ALIASES:
            return LABEL_ALIASES[canonical]

        return raw_label.replace("_", " ").replace("-", " ").title()

    def _canonical_label(self, raw_label: str) -> str:
        return raw_label.lower().replace("-", "_").replace(" ", "_")

    def _is_positive_label(self, canonical_label: str) -> bool:
        return canonical_label in POSITIVE_CANONICAL_LABELS

    def _is_negative_label(self, canonical_label: str) -> bool:
        return canonical_label in NEGATIVE_CANONICAL_LABELS

    def _resolve_toxic_score(self, scores: list[dict[str, Any]]) -> float:
        if not scores:
            return 0.0

        positive_scores = [entry["score"] for entry in scores if self._is_positive_label(entry["canonicalLabel"])]
        negative_scores = [entry["score"] for entry in scores if self._is_negative_label(entry["canonicalLabel"])]

        if positive_scores:
            if negative_scores:
                return max(positive_scores)
            return max(positive_scores)

        if negative_scores:
            return max(0.0, 1 - max(negative_scores))

        return scores[0]["score"]

    def _build_summary(self, is_toxic: bool, primary_signal: str, top_score: float) -> str:
        if is_toxic:
            if top_score >= 0.85:
                return f"The local model found a strong {primary_signal.lower()} signal in this comment."
            return f"The local model detected a meaningful {primary_signal.lower()} pattern that may require moderation."

        if top_score <= 0.15:
            return "The local model found very little evidence of toxicity in this comment."
        return "The local model found some weak toxicity cues, but not enough to flag the comment."

    def _build_recommendation(self, is_toxic: bool, top_score: float) -> str:
        if is_toxic and top_score >= 0.85:
            return "Queue this comment for review or block it before publishing."
        if is_toxic:
            return "Consider flagging this comment for moderator review or asking for a rewrite."
        return "This comment is likely safe to pass through, though you can still review edge cases manually."
