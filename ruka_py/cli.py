"""Interactive collision-object editor."""

from .robot import RukaRobot

SHAPES = ("box", "sphere", "cylinder", "cone")


def _read_numbers(prompt: str, count: int) -> list[float]:
    while True:
        try:
            values = [float(value) for value in input(prompt).split()]
        except ValueError:
            values = []
        if len(values) == count:
            return values
        print(f"Введите {count} чисел через пробел")


def main() -> None:
    """Run the interactive collision-object editor."""

    with RukaRobot() as robot:
        while True:
            action = input("Действие (add, remove, move, end): ").strip().lower()
            if action == "end":
                return
            if action not in {"add", "remove", "move"}:
                print("Допустимые действия: add, remove, move, end")
                continue

            object_id = input("ID объекта (например box_1): ").strip()
            shape = object_id.split("_", maxsplit=1)[0]
            if shape not in SHAPES:
                print(f"ID должен начинаться с: {', '.join(SHAPES)}")
                continue

            if action == "remove":
                robot.remove_collision_object(object_id)
                continue

            position = _read_numbers("Position [x y z]: ", 3)
            orientation = _read_numbers("Orientation [x y z w]: ", 4)
            if action == "move":
                robot.move_collision_object(object_id, position, orientation)
                continue

            dimensions = _read_numbers("Dimensions [x y z]: ", 3)
            if shape == "box":
                robot.add_box(object_id, position, orientation, dimensions)
            elif shape == "sphere":
                robot.add_sphere(object_id, position, dimensions[0])
            elif shape == "cylinder":
                robot.add_cylinder(
                    object_id, position, orientation, dimensions[0], dimensions[1]
                )
            else:
                robot.add_cone(
                    object_id, position, orientation, dimensions[0], dimensions[1]
                )


if __name__ == "__main__":
    main()
