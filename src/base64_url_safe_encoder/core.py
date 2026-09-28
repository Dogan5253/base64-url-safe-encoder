"""URL-safe Base64 encoding and decoding without padding.

The stdlib `base64.urlsafe_b64encode` produces output padded with '=' to a
length that is a multiple of four. That padding is legal in a URL query string
but '=' is also a common delimiter and several routing libraries treat it
specially, so we strip it. RFC 4648 §3.2 permits decoders to accept unpadded
input; the stdlib decoder does not, so we re-pad before delegating to it.
"""

from __future__ import annotations

import base64


def encode(data: bytes) -> str:
    """Encode bytes to an unpadded URL-safe Base64 string.

    Returns a `str`, not `bytes`, because the output is meant to be embedded in
    URLs and JSON. Returning `str` avoids a `.decode()` call at every call site.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"expected bytes-like, got {type(data).__name__}")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def decode(text: str | bytes) -> bytes:
    """Decode a URL-safe Base64 string, with or without padding.

    Accepts `str` or `bytes` for the input because both forms appear in the
    wild (HTTP headers arrive as `str`, raw socket payloads as `bytes`).
    Raises `ValueError` if the input contains characters outside the URL-safe
    Base64 alphabet or has a length that cannot be padded to a multiple of four.
    """
    if isinstance(text, str):
        raw = text.encode("ascii")
    elif isinstance(text, (bytes, bytearray)):
        raw = bytes(text)
    else:
        raise TypeError(f"expected str or bytes-like, got {type(text).__name__}")

    # Reject standard-alphabet characters '+' and '/' explicitly. The stdlib
    # b64decode with altchars=b'-_' treats '+' and '/' as valid because they
    # are part of the standard alphabet; altchars only specifies the URL-safe
    # substitutes, it does not forbid the originals. Silently accepting them
    # would mask data encoded with the wrong alphabet.
    if b"+" in raw or b"/" in raw:
        raise ValueError("input contains standard-alphabet characters '+' or '/'")

    # base64.b64decode with validate=True rejects characters outside the
    # alphabet. We pass altchars=b'-_' so it accepts the URL-safe alphabet.
    # We re-pad to a multiple of four because b64decode requires it when
    # validate=True is combined with non-padded input on some CPython versions.
    remainder = len(raw) % 4
    if remainder:
        raw += b"=" * (4 - remainder)

    try:
        return base64.b64decode(raw, altchars=b"-_", validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        # binascii.Error is a subclass of ValueError in modern Python, but we
        # catch both to be explicit and to normalise the error type.
        raise ValueError(str(exc)) from exc
