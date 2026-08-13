import logging

from domain.types import FingerPrint

logger = logging.getLogger(__name__)


def match_fingerprint(
    scanned: FingerPrint,
    fingerprint: FingerPrint,
    *,
    tolerance: int = 8,
) -> bool:
    """Match sample points to a reference fingerprint.

    Compares colors in order (spatial layout matters). Each RGB channel may
    differ by at most ``tolerance``. True matches on reference shots are
    within ~2; unrelated UI is typically 150+.
    """
    if len(scanned) != len(fingerprint):
        return False

    for sample, reference in zip(scanned, fingerprint, strict=True):
        if any(
            abs(sample_c - reference_c) > tolerance
            for sample_c, reference_c in zip(sample, reference, strict=True)
        ):
            return False
    return True
