# coding=utf-8
"""Add tappable ntfy notification actions without changing channel payload rendering."""

from __future__ import annotations

import re
from functools import wraps
from typing import Any, Callable, Dict


_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
_BARE_URL_RE = re.compile(r"https?://[^\s<>\])]+")
_WRAPPED_ATTR = "_trendradar_ntfy_click_wrapped"


def _extract_urls_from_text(text: str, quote_uri: Callable[[str], str], limit: int = 3) -> list[str]:
    """Extract unique URLs from markdown links and bare URLs in display order."""
    urls: list[str] = []
    seen: set[str] = set()

    def add(url: str) -> None:
        url = quote_uri(url.rstrip(".,;:"))
        if url and url not in seen:
            seen.add(url)
            urls.append(url)

    matches: list[tuple[int, str]] = []
    for match in _MARKDOWN_LINK_RE.finditer(text):
        matches.append((match.start(), match.group(1)))
    for match in _BARE_URL_RE.finditer(text):
        matches.append((match.start(), match.group(0)))

    for _, url in sorted(matches, key=lambda item: item[0]):
        add(url)
        if len(urls) >= limit:
            break

    return urls


def _add_ntfy_click_headers(headers: Dict[str, str], content: str, quote_uri: Callable[[str], str]) -> Dict[str, str]:
    """Return headers with ntfy click/actions pointing at the first few news links."""
    urls = _extract_urls_from_text(content, quote_uri)
    if not urls:
        return headers

    updated_headers = dict(headers)
    updated_headers.setdefault("Click", urls[0])
    updated_headers.setdefault(
        "Actions",
        "; ".join(f"view, Open {index}, {url}" for index, url in enumerate(urls, start=1)),
    )
    return updated_headers


class _RequestsProxy:
    def __init__(self, requests_module: Any):
        self._requests_module = requests_module

    def __getattr__(self, name: str) -> Any:
        return getattr(self._requests_module, name)

    def post(self, url: str, *args: Any, **kwargs: Any) -> Any:
        headers = kwargs.get("headers")
        data = kwargs.get("data")
        if isinstance(headers, dict) and data:
            if isinstance(data, bytes):
                content = data.decode("utf-8", errors="ignore")
            else:
                content = str(data)
            kwargs["headers"] = _add_ntfy_click_headers(headers, content, self._requests_module.utils.requote_uri)

        return self._requests_module.post(url, *args, **kwargs)


def enable_ntfy_click_headers(senders_module: Any) -> Callable[..., bool]:
    """Wrap send_to_ntfy so mobile ntfy clients can open links from notifications."""
    send_to_ntfy = senders_module.send_to_ntfy
    if getattr(send_to_ntfy, _WRAPPED_ATTR, False):
        return send_to_ntfy

    @wraps(send_to_ntfy)
    def wrapped_send_to_ntfy(*args: Any, **kwargs: Any) -> bool:
        original_requests = senders_module.requests
        senders_module.requests = _RequestsProxy(original_requests)
        try:
            return send_to_ntfy(*args, **kwargs)
        finally:
            senders_module.requests = original_requests

    setattr(wrapped_send_to_ntfy, _WRAPPED_ATTR, True)
    senders_module.send_to_ntfy = wrapped_send_to_ntfy
    return wrapped_send_to_ntfy
