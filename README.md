# base64-url-safe-encoder

Encodes bytes to an unpadded URL-safe Base64 string and decodes both padded and unpadded input.

```python
from base64_url_safe_encoder import encode, decode

token = encode(b"\x01\x02\x03")  # 'AQID'
raw = decode(token)               # b'\x01\x02\x03'
```

## Why

The standard library's `base64.urlsafe_b64encode` appends `=` padding so the output length is a multiple of four. That padding is technically valid in a URL but `=` is treated as a delimiter by several routing and query-string libraries, which leads to silently truncated tokens. This library strips padding on encode and restores it on decode before delegating to the stdlib, so callers never handle `=` themselves.

The trade-off: the encoder only produces unpadded output. If you need padded output for interop with a system that requires it, use `base64.urlsafe_b64encode` directly instead.

## Edge cases

- `decode` accepts both `str` and `bytes` because HTTP headers arrive as `str` but raw socket payloads arrive as `bytes`.
- `decode` raises `ValueError` on inputs containing `+` or `/` (standard-alphabet characters), because silently accepting them would mask data that was likely encoded with the wrong alphabet.
- A single-character input like `"A"` is rejected: after padding to four characters it would decode, but one character is not a valid Base64 group and indicates a truncated or corrupted token.

## Exports

- `encode(data: bytes) -> str`
- `decode(text: str | bytes) -> bytes`
