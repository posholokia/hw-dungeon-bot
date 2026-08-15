"""
Калибровка параметра tolerance при сравнении отпечатков титанов
между собой. Рекомендуется ставить значение в 2 раза меньше чем то,
на котором появляется коллизия минус 1. Чтобы цвет по середине
не мог быть отнесен к обоим титанам.
"""

import math

from core.depends.container import get_container
from services.fingerprint_match import match_fingerprint
from services.titan_catalog import TitanCatalog

container = get_container()
catalog = container.get(TitanCatalog)
titans = list(catalog.get_titans().values())


def check_collision(tolerance: int) -> bool:
    for titan in titans:
        for inner in titans:
            if titan.name == inner.name:
                continue

            if match_fingerprint(
                titan.fingerprint, inner.fingerprint, tolerance=tolerance
            ):
                print(f"Tolerance ({tolerance}) {titan.name} == {inner.name}")
                return True

    return False


if __name__ == "__main__":
    collision = False
    iterations = 0
    tolerance = 0

    while not collision:
        tolerance += 1
        iterations += 1
        collision = check_collision(tolerance)

        if iterations == 255:
            break

    print(
        f"Рекомендуемое максимальное значение tolerance: {math.floor(tolerance / 2) - 1}"
    )
