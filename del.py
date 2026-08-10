# import json
# from pathlib import Path
# from PIL import Image
# import numpy as np

# from services.fingerprint_match import match_fingerprint


# water_path = "trash/flow/team_water.png"
# fire_path = "trash/flow/team_fire.png"
# common_path = "trash/flow/team_common_v1.png"
# earth_path = "trash/flow/team_earth.png"



# cords = {
#     1: [176, 905],
#     2: [307, 905],
#     3: [439, 905],
#     4: [570, 905],
#     5: [702, 905]
# }


# w = 40
# h = 40


# def take_print(img, points):
#     fingerprint = [
#         tuple(int(c) for c in img[y, x, :3])  # RGB
#         for x, y in points
#     ]
#     return fingerprint

# match_water = {
#     1: "Гиперион",
#     2: "Маири",
#     3: "Тидус",
#     4: "Нова",
#     5: "Сигурд"
# }

# match_fire = {
#     1: "Игнис",
#     2: "Ашерона",
#     3: "Араджи",
#     4: "Вулкан",
#     5: "Молох"
# }

# match_common = {
#     1: "Гиперион",
#     2: "Ияри",
#     3: "Араджи",
#     4: "Ангус",
#     5: "Сигурд"
# }

# match_earth = {
#     1: "Сильва",
#     2: "Эдем",
#     3: "Вердок",
#     4: "Авалон",
#     5: "Ангус"
# }

# def get_fingerprint(match, img_path) -> dict[str, list[tuple[int, int, int]]]:
#     result: dict[str, list[tuple[int, int, int]]] = {}
#     for t, c in cords.items():
#         x = c[0]
#         y = c[1]
#         img = Image.open(img_path)
#         img = img.convert("RGB")
#         img = np.asarray(img)
#         p1 = x + 12, y + 33
#         p2 = x + 22, y + 21
#         p3 = x + 6, y + 40
#         p4 = x + 21, y + 1
#         p5 = x + 20, y + 37
#         points = [p1, p2, p3, p4, p5]
#         print(points)
#         fingerprint = take_print(img, points)
#         result[match[t]] = fingerprint
#         paint_check_points(img_path, points, (255, 0, 0))
#     return result


# def find_unique_fingerprint(fingerprints: dict[str, list[tuple[int, int, int]]]) -> list[str]:
#     titans = len(fingerprints.keys())
#     points = []
#     for p_idx in range(1600):
#         prints = set()
#         for f in fingerprints.values():
#             prints.add(tuple(f))
#         if len(prints) == titans:
#             points.append(p_idx)
#     return points

# def main():
#     wf = get_fingerprint(match_water, water_path)
#     ff = get_fingerprint(match_fire, fire_path)
#     cf = get_fingerprint(match_common, common_path)
#     ef = get_fingerprint(match_earth, earth_path)
#     res = {}

#     res.update(wf)
#     res.update(ff)
#     res.update(cf)
#     res.update(ef)
#     with open("fingerprint.json", "w") as f:
#         json.dump(res, f, indent=4, ensure_ascii=False)

#     points = find_unique_fingerprint(res)
#     print(len(points))


# def paint_check_points(
#     img_path: str,
#     points: list[tuple[int, int]],
#     color: tuple[int, int, int] = (255, 0, 0),
# ) -> str:
#     """Перекрашивает заданные пиксели и сохраняет копию с суффиксом _check."""
#     path = Path(img_path)
#     img = Image.open(path).convert("RGB")
#     arr = np.asarray(img).copy()
#     h, w = arr.shape[:2]
#     for x, y in points:
#         if 0 <= x < w and 0 <= y < h:
#             arr[y, x] = color
#     out = path.with_name(f"{path.stem}_check{path.suffix}")
#     Image.fromarray(arr).save(out)
#     return str(out)
    

# def check_f():
#     x = 177
#     y = 331
#     matched = []
#     img = Image.open("trash/flow/araji.png")
#     img = img.convert("RGB")
#     img = np.asarray(img)
#     p1 = x + 12, y + 33
#     p2 = x + 22, y + 21
#     p3 = x + 6, y + 40
#     p4 = x + 21, y + 1
#     p5 = x + 20, y + 37
#     points = [p1, p2, p3, p4, p5]

#     fingerprint = take_print(img, points)
    
#     with open("fingerprint.json", "r") as f:
#         fingerprints = json.load(f)

#     target_f = fingerprints["Араджи"]

#     if match_fingerprint(fingerprint, target_f, tolerance=8):
#         matched.append((x, y))

#     print(matched)
#     if not matched:
#         paint_check_points("trash/flow/araji.png", points, (255, 0, 0))


# def save_titans():
#     with open("fingerprint.json", "r") as f:
#         fingerprints = json.load(f)
    
#     res = {}
#     for k, v in fingerprints.items():
#         res[v] = k
    
#     with open("totans.py", "w") as f:
#         json.dump(fingerprints, f, indent=4, ensure_ascii=False)


# def get_points():
#     for t, c in cords.items():
#         x = c[0]
#         y = c[1]
#         p1 = x + 12, y + 33
#         p2 = x + 22, y + 21
#         p3 = x + 6, y + 40
#         p4 = x + 21, y + 1
#         p5 = x + 20, y + 37
#         points = [p1, p2, p3, p4, p5]
#         print(points)

# if __name__ == "__main__":
#     # main()
#     # check_f()
#     # get_fingerprint(match_water, water_path)
#     # save_titans()
#     get_points()

import copy

class Titan:
    def __init__(self, position: int, name: str) -> None:
        self.position = position
        self.name = name

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, value: object, /) -> bool:
        return self.name == value.name and self.position == value.position

    def __hash__(self) -> int:
        return hash(self.name)


class _TitanList:
    def __init__(self, titans: list["Titan"]) -> None:
        self._titans = titans
        self._titan_position_map = {}
        for i in range(1, len(titans) + 1):
            self._titan_position_map[i] = titans[i - 1]
        
        self.__idx = 0

    def delete_titan(self, name: str) -> None:
        c = 1
        new_map = {}
        for titan in self._titan_position_map.values():
            if name == titan.name:
                continue
            new_map[c] = titan
            c += 1
        self._titan_position_map = new_map

    def add_titan(self, new_titan: Titan) -> None:
        new_map = {}
        titans = list(self._titan_position_map.values())
        titans.append(new_titan)
        titans.sort(key=lambda x: x.position)
        for i in range(1, len(titans) + 1):
            new_map[i] = titans[i - 1]
        self._titan_position_map = new_map

    def __next__(self):
        try:
            value = self._titan_position_map[self.__idx + 1]
        except KeyError:
            raise StopIteration()
        
        self.__idx += 1
        return value

    def __iter__(self):
        self.__idx = 0
        return self

    def __len__(self) -> int:
        return len(self._titan_position_map)

    def __getitem__(self, index: int) -> Titan:
        try:
            return self._titan_position_map[index + 1]
        except KeyError:
            raise IndexError("Index out of range")

    def __repr__(self) -> str:
        return f"{[titan for titan in sorted(self._titan_position_map.values(), key=lambda x: x.position)]}"


titan_position_map = {
    1: Titan(2, "Второй"),
    2: Titan(4, "Четвертый"),
    3: Titan(6, "Шестой")
}

current = _TitanList(
    [
        Titan(1, "Первый"),
        Titan(2, "Второй"),
        Titan(4, "Четвертый"),
        Titan(6, "Шестой"),
        Titan(10, "Десятый"),
    ]
)

expected = _TitanList(
    [
        Titan(4, "Четвертый"),
        Titan(6, "Шестой"),
    ]
)

current_positions = {t.position: t for t in current}
expected_positions = {t.position: t for t in expected}
titans_by_position = {}
titans_by_position.update(expected_positions)
titans_by_position.update(current_positions)

all_positions = list(titans_by_position.keys())
all_positions.sort()
print(all_positions)

c = 0

click_order = []

for i, pos in enumerate(all_positions):
    if pos in expected_positions and pos not in current_positions:
        continue
    elif pos in expected_positions and pos in current_positions:
        c += 1
        continue
    elif pos not in expected_positions and pos in current_positions:
        click_order.append(c)
        continue

print(click_order)

# first = Titan(1, "Первый")
# third = Titan(3, "Третий")
# five = Titan(5, "Пятый")
# last = Titan(10, "Десятый")


# def add_titan(new_titan: Titan) -> None:
#     t_map = copy.deepcopy(titan_position_map)
#     new_map = {}
#     titans = list(t_map.values())
#     titans.append(new_titan)
#     titans.sort(key=lambda x: x.position)

#     for i in range(1, len(titans) + 1):
#         new_map[i] = titans[i - 1]
#     return new_map


# t1 = add_titan(first)
# assert t1 == {
#     1: Titan(1, "Первый"),
#     2: Titan(2, "Второй"),
#     3: Titan(4, "Четвертый"),
#     4: Titan(6, "Шестой")
# }, f"{t1}"

# t2 = add_titan(third)
# assert t2 == {
#     1: Titan(2, "Второй"),
#     2: Titan(3, "Третий"),
#     3: Titan(4, "Четвертый"),
#     4: Titan(6, "Шестой")
# }, f"{t2}"

# t3 = add_titan(five)
# assert t3 == {
#     1: Titan(2, "Второй"),
#     2: Titan(4, "Четвертый"),
#     3: Titan(5, "Пятый"),
#     4: Titan(6, "Шестой")
# }, f"{t3}"

# t4 = add_titan(last)
# assert t4 == {
#     1: Titan(2, "Второй"),
#     2: Titan(4, "Четвертый"),
#     3: Titan(6, "Шестой"),
#     4: Titan(10, "Десятый"),
# }, f"{t4}"
