"""
TuringBitCompression (TBC) — prototype stub
See README.md for algorithm description.
"""


def encode(data: bytes, k: int = 2) -> bytes:
    """Encode bytes using TBC indicator-plane coding.

    Args:
        data: raw input bytes
        k: n-gram size in bits (default 2, alphabet size = 2^k)

    Returns:
        compressed representation (format TBD)

    Raises:
        NotImplementedError: implementation pending
    """
    raise NotImplementedError("TBC encoder not yet implemented — see README.md")


def decode(compressed: bytes) -> bytes:
    """Decode TBC-compressed bytes.

    Raises:
        NotImplementedError: implementation pending
    """
    raise NotImplementedError("TBC decoder not yet implemented — see README.md")
