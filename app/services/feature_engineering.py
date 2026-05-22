from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import re
from typing import Dict
from urllib.parse import urlparse

from networksecurity.constant.training_pipeline import TARGET_COLUMN


EXPECTED_FEATURES = [
    "having_IP_Address",
    "URL_Length",
    "Shortining_Service",
    "having_At_Symbol",
    "double_slash_redirecting",
    "Prefix_Suffix",
    "having_Sub_Domain",
    "SSLfinal_State",
    "Domain_registeration_length",
    "Favicon",
    "port",
    "HTTPS_token",
    "Request_URL",
    "URL_of_Anchor",
    "Links_in_tags",
    "SFH",
    "Submitting_to_email",
    "Abnormal_URL",
    "Redirect",
    "on_mouseover",
    "RightClick",
    "popUpWidnow",
    "Iframe",
    "age_of_domain",
    "DNSRecord",
    "web_traffic",
    "Page_Rank",
    "Google_Index",
    "Links_pointing_to_page",
    "Statistical_report",
]

SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "buff.ly",
    "is.gd",
}


@dataclass(frozen=True)
class FeaturePayload:
    url: str
    features: Dict[str, float]


def _signed_value(condition: bool, positive: int = 1, negative: int = -1) -> int:
    return positive if condition else negative


def _subdomain_score(hostname: str) -> int:
    parts = [part for part in hostname.split(".") if part]
    if len(parts) <= 2:
        return 1
    if len(parts) == 3:
        return 0
    return -1


def _resolve_dns(hostname: str) -> int:
    if not hostname:
        return -1
    try:
        import socket

        socket.gethostbyname(hostname)
        return 1
    except Exception:
        return -1


def extract_url_features(url: str) -> Dict[str, int]:
    parsed = urlparse(url if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url) else f"https://{url}")
    hostname = (parsed.hostname or "").lower()
    domain = hostname or parsed.netloc.lower()
    url_length = len(url)

    try:
        ipaddress.ip_address(hostname)
        is_ip = True
    except Exception:
        is_ip = False

    return {
        "having_IP_Address": _signed_value(is_ip),
        "URL_Length": 1 if url_length < 54 else 0 if url_length < 75 else -1,
        "Shortining_Service": -1 if any(domain.endswith(shortener) for shortener in SHORTENER_DOMAINS) else 1,
        "having_At_Symbol": -1 if "@" in url else 1,
        "double_slash_redirecting": -1 if url.replace("http://", "", 1).replace("https://", "", 1).find("//") != -1 else 1,
        "Prefix_Suffix": -1 if "-" in hostname else 1,
        "having_Sub_Domain": _subdomain_score(hostname),
        "SSLfinal_State": 1 if parsed.scheme == "https" else -1,
        "Domain_registeration_length": 0,
        "Favicon": 1,
        "port": -1 if parsed.port and parsed.port not in {80, 443} else 1,
        "HTTPS_token": -1 if "https" in hostname and parsed.scheme != "https" else 1,
        "Request_URL": 1,
        "URL_of_Anchor": 0,
        "Links_in_tags": 0,
        "SFH": 0,
        "Submitting_to_email": -1 if "mailto:" in url.lower() else 1,
        "Abnormal_URL": -1 if "@" in parsed.netloc or is_ip else 1,
        "Redirect": 0,
        "on_mouseover": 1,
        "RightClick": 1,
        "popUpWidnow": 1,
        "Iframe": 1,
        "age_of_domain": 0,
        "DNSRecord": _resolve_dns(hostname),
        "web_traffic": 0,
        "Page_Rank": 0,
        "Google_Index": 1,
        "Links_pointing_to_page": 0,
        "Statistical_report": 0,
    }


def normalize_feature_payload(url: str | None, features: Dict[str, float] | None) -> FeaturePayload:
    if features:
        normalized = {name: float(features.get(name, 0.0)) for name in EXPECTED_FEATURES}
        return FeaturePayload(url=url or "feature-input", features=normalized)

    if not url:
        raise ValueError("Either a raw URL or a feature map is required.")

    derived = extract_url_features(url)
    return FeaturePayload(url=url, features={name: float(derived.get(name, 0.0)) for name in EXPECTED_FEATURES})


def feature_frame_columns() -> list[str]:
    return [column for column in EXPECTED_FEATURES if column != TARGET_COLUMN]
