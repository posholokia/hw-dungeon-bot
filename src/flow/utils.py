def match_fingerprint(
    scanned: list[tuple[int, int, int]],
    fingerprint: list[tuple[int, int, int]]
) -> bool:
    for s, f in zip(scanned, fingerprint, strict=True):
        for s_c, f_c in zip(s, f, strict=True):
            if s_c - f_c > 1:
                return False
    return True
