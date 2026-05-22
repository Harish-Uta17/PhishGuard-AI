from __future__ import annotations


def threat_profile(prediction: int, confidence: float) -> tuple[str, str, float]:
    confidence = max(0.0, min(float(confidence), 1.0))

    if int(prediction) == 1:
        if confidence >= 0.9:
            return "Safe", "Benign", confidence
        if confidence >= 0.75:
            return "Low", "Benign", confidence
        return "Moderate", "Review", confidence

    if confidence >= 0.9:
        return "Critical", "Phishing", confidence
    if confidence >= 0.75:
        return "High", "Phishing", confidence
    return "Elevated", "Suspicious", confidence
