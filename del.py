import json
from pathlib import Path
from PIL import Image
import numpy as np

from services.fingerprint_match import match_fingerprint


water_path = "trash/flow/team_water.png"
fire_path = "trash/flow/team_fire.png"
common_path = "trash/flow/team_common_v1.png"
earth_path = "trash/flow/team_earth.png"



cords = {
    1: [176, 905],
    2: [307, 905],
    3: [439, 905],
    4: [570, 905],
    5: [702, 905]
}


w = 40
h = 40


def take_print(img, points):
    fingerprint = [
        tuple(int(c) for c in img[y, x, :3])  # RGB
        for x, y in points
    ]
    return fingerprint

match_water = {
    1: "Гиперион",
    2: "Маири",
    3: "Тидус",
    4: "Нова",
    5: "Сигурд"
}

match_fire = {
    1: "Игнис",
    2: "Ашерона",
    3: "Араджи",
    4: "Вулкан",
    5: "Молох"
}

match_common = {
    1: "Гиперион",
    2: "Ияри",
    3: "Араджи",
    4: "Ангус",
    5: "Сигурд"
}

match_earth = {
    1: "Сильва",
    2: "Эдем",
    3: "Вердок",
    4: "Авалон",
    5: "Ангус"
}

def get_fingerprint(match, img_path) -> dict[str, list[tuple[int, int, int]]]:
    result: dict[str, list[tuple[int, int, int]]] = {}
    for t, c in cords.items():
        x = c[0]
        y = c[1]
        img = Image.open(img_path)
        img = img.convert("RGB")
        img = np.asarray(img)
        p1 = x + 12, y + 33
        p2 = x + 22, y + 21
        p3 = x + 6, y + 40
        p4 = x + 21, y + 1
        p5 = x + 20, y + 37
        points = [p1, p2, p3, p4, p5]
        print(points)
        fingerprint = take_print(img, points)
        result[match[t]] = fingerprint
        paint_check_points(img_path, points, (255, 0, 0))
    return result


def find_unique_fingerprint(fingerprints: dict[str, list[tuple[int, int, int]]]) -> list[str]:
    titans = len(fingerprints.keys())
    points = []
    for p_idx in range(1600):
        prints = set()
        for f in fingerprints.values():
            prints.add(tuple(f))
        if len(prints) == titans:
            points.append(p_idx)
    return points

def main():
    wf = get_fingerprint(match_water, water_path)
    ff = get_fingerprint(match_fire, fire_path)
    cf = get_fingerprint(match_common, common_path)
    ef = get_fingerprint(match_earth, earth_path)
    res = {}

    res.update(wf)
    res.update(ff)
    res.update(cf)
    res.update(ef)
    with open("fingerprint.json", "w") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)

    points = find_unique_fingerprint(res)
    print(len(points))


def paint_check_points(
    img_path: str,
    points: list[tuple[int, int]],
    color: tuple[int, int, int] = (255, 0, 0),
) -> str:
    """Перекрашивает заданные пиксели и сохраняет копию с суффиксом _check."""
    path = Path(img_path)
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img).copy()
    h, w = arr.shape[:2]
    for x, y in points:
        if 0 <= x < w and 0 <= y < h:
            arr[y, x] = color
    out = path.with_name(f"{path.stem}_check{path.suffix}")
    Image.fromarray(arr).save(out)
    return str(out)
    

def check_f():
    x = 177
    y = 331
    matched = []
    img = Image.open("trash/flow/araji.png")
    img = img.convert("RGB")
    img = np.asarray(img)
    p1 = x + 12, y + 33
    p2 = x + 22, y + 21
    p3 = x + 6, y + 40
    p4 = x + 21, y + 1
    p5 = x + 20, y + 37
    points = [p1, p2, p3, p4, p5]

    fingerprint = take_print(img, points)
    
    with open("fingerprint.json", "r") as f:
        fingerprints = json.load(f)

    target_f = fingerprints["Араджи"]

    if match_fingerprint(fingerprint, target_f, tolerance=8):
        matched.append((x, y))

    print(matched)
    if not matched:
        paint_check_points("trash/flow/araji.png", points, (255, 0, 0))


def save_titans():
    with open("fingerprint.json", "r") as f:
        fingerprints = json.load(f)
    
    res = {}
    for k, v in fingerprints.items():
        res[v] = k
    
    with open("totans.py", "w") as f:
        json.dump(fingerprints, f, indent=4, ensure_ascii=False)


def get_points():
    for t, c in cords.items():
        x = c[0]
        y = c[1]
        p1 = x + 12, y + 33
        p2 = x + 22, y + 21
        p3 = x + 6, y + 40
        p4 = x + 21, y + 1
        p5 = x + 20, y + 37
        points = [p1, p2, p3, p4, p5]
        print(points)

if __name__ == "__main__":
    # main()
    # check_f()
    # get_fingerprint(match_water, water_path)
    # save_titans()
    get_points()