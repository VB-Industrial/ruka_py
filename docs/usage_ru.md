# Руководство пользователя `ruka_py`

Библиотека `ruka_py` предназначена для управления
манипулятором RUKA через ROS 2, MoveIt 2 и `pymoveit2`.

Пользователю не нужно самостоятельно:

- вызывать `rclpy.init()` и `rclpy.shutdown()`;
- создавать ROS-ноду и executor;
- запускать отдельный поток executor;
- создавать `MoveIt2`;
- формировать сообщения `JointTrajectory` и `JointTrajectoryPoint`.

В пользовательском скрипте остаются конфигурация конкретного манипулятора,
координаты, углы, время и команды движения.

## 1. Подготовка окружения

До запуска пользовательского скрипта должны быть запущены драйверы робота или
симулятор, `robot_state_publisher`, контроллеры и MoveIt 2. Используйте launch-файл
вашей конфигурации RUKA.

В каждом новом терминале подключите ROS 2 и собранный workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ws_ruka/install/setup.bash
```

Проверить доступность `pymoveit2` можно командой:

```bash
python3 -c "import pymoveit2; print('pymoveit2 доступен')"
```

Если появляется `ModuleNotFoundError`, workspace не собран или не выполнена
команда `source ~/ws_ruka/install/setup.bash`.

## 2. Установка библиотеки

Рекомендуется создать виртуальное окружение с доступом к системным пакетам
ROS, затем установить библиотеку из клона репозитория:

```bash
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

cd ~/ruka_py
python3 -m pip install .
```

Для разработки используйте editable-режим и дополнительные инструменты:

```bash
python3 -m pip install -e ".[dev]"
```

После публикации тега библиотеку можно установить напрямую с GitHub:

```bash
python3 -m pip install \
  "ruka_py @ git+https://github.com/VB-Industrial/ruka_py.git@v0.2.0"
```

Проверка установки:

```bash
python3 -c "import ruka_py; print(ruka_py.__version__)"
```

## 3. Минимальный пользовательский скрипт

Имена суставов у разных манипуляторов различаются. Поэтому библиотека не
содержит имён по умолчанию и не пытается угадывать их по `/joint_states`, где
могут одновременно присутствовать захват, колёса и дополнительные оси.

Создайте Python-файл, например `my_motion.py`, и явно задайте имена из URDF,
SRDF и конфигурации контроллера:

```python
from ruka_py import RobotConfig, RukaRobot

config = RobotConfig(
    joint_names=(
        "shoulder_joint",
        "upper_arm_joint",
        "elbow_joint",
        "wrist_1_joint",
        "wrist_2_joint",
        "wrist_3_joint",
    ),
    base_link_name="base_link",
    end_effector_name="tool_link",
    group_name="arm",
)

with RukaRobot(config) as robot:
    robot.move_to_angles([0.0, -1.57, 1.57, 0.0, 0.0, 0.0])
```

Порядок `joint_names` должен точно совпадать с порядком, ожидаемым контроллером.
Количество суставов не зафиксировано библиотекой. Все последующие фрагменты
инструкции предполагают, что переменная `config` создана таким способом.

Запустите его в терминале с подключённым ROS-окружением:

```bash
python3 my_motion.py
```

Конструкция `with RukaRobot(config) as robot` обязательна для рекомендуемого способа
работы. При выходе из блока библиотека корректно остановит executor и освободит
ROS-ресурсы, даже если во время выполнения возникнет ошибка.

## 4. Движение по углам суставов

Углы задаются в радианах. Число значений должно совпадать с числом элементов в
`config.joint_names`:

```python
from ruka_py import RukaRobot


with RukaRobot(config) as robot:
    joint_goal = [0.0, -1.57, 1.57, 0.0, 0.0, 0.0]
    robot.move_to_angles(joint_goal)
```

Библиотека передаёт углы контроллеру в том же порядке, в котором суставы
перечислены в `config.joint_names`.

По умолчанию метод ждёт завершения движения. Для асинхронной отправки команды
можно указать `wait=False`:

```python
robot.move_to_angles(joint_goal, wait=False)
```

## 5. Движение по позиции и ориентации

Позиция задаётся в метрах в формате `[x, y, z]`. Ориентация задаётся
кватернионом в формате `[x, y, z, w]`. Библиотека автоматически нормализует
ненулевой кватернион:

```python
from ruka_py import RukaRobot


with RukaRobot(config) as robot:
    position = [0.256, 0.0, 0.5628]
    orientation = [0.0, 0.0, 0.0, 1.0]
    robot.move_to_pose(position, orientation)
```

Если ориентация известна в углах Эйлера, её можно перевести в кватернион.
Аргументы передаются в градусах в порядке `roll`, `pitch`, `yaw`:

```python
from ruka_py import RukaRobot, euler_deg_to_quaternion


orientation = euler_deg_to_quaternion(0, 0, 90)

with RukaRobot(config) as robot:
    robot.move_to_pose([0.256, 0.0, 0.5628], orientation)
```

## 6. Траектория по углам суставов

Каждая точка состоит из двух элементов:

```text
(время_от_начала_в_секундах, [углы в порядке config.joint_names])
```

Пример:

```python
from ruka_py import RukaRobot


trajectory = [
    (0.5, [0.0, -1.57, 1.57, 0.0, 0.0, 0.0]),
    (3.0, [0.2, -1.40, 1.30, 0.0, 0.1, 0.0]),
    (5.5, [0.4, -1.20, 1.10, 0.0, 0.2, 0.0]),
]

with RukaRobot(config) as robot:
    # Сначала доезжаем до первой точки.
    robot.move_to_angles(trajectory[0][1])

    # Затем выполняем собранную траекторию.
    robot.execute_angle_trajectory(trajectory)
```

Время считается от начала траектории, а не между соседними точками. Оно должно
быть неотрицательным и строго возрастать: `0.5`, `3.0`, `5.5`.

## 7. Траектория по позициям и ориентациям

Каждая точка состоит из трёх элементов:

```text
(время_от_начала, [x, y, z], [qx, qy, qz, qw])
```

Пример:

```python
from ruka_py import RukaRobot


trajectory = [
    (0.5, [0.45299, -0.10155, 0.46503],
     [0.70172, 0.010648, 0.71223, 0.014095]),
    (4.5, [0.25299, 0.03015, 0.26503],
     [0.70172, 0.010648, 0.71223, 0.014095]),
    (6.0, [0.35299, -0.10155, 0.46503],
     [0.70172, 0.010648, 0.71223, 0.014095]),
]

with RukaRobot(config) as robot:
    _, first_position, first_orientation = trajectory[0]
    robot.move_to_pose(first_position, first_orientation)
    robot.execute_pose_trajectory(trajectory)
```

Для каждой точки библиотека вызывает обратную кинематику MoveIt. Если решение
не найдено, будет выброшено исключение `RuntimeError` с указанием проблемной
позиции.

## 8. Чтение траектории из CSV

Функция `read_csv()` возвращает таблицу pandas `DataFrame`:

```python
from ruka_py import read_csv


data = read_csv("/полный/путь/trajectory.csv")
print(data.shape)
print(data.head())
```

В этом конкретном примере для шестикоординатного робота ожидается семь столбцов:

```text
time, joint_1, joint_2, joint_3, joint_4, joint_5, joint_6
```

Полный пример:

```python
from pathlib import Path

from ruka_py import RukaRobot, read_csv


csv_file = Path.home() / "Desktop" / "data_csv_ruka_fk" / "UDRIVEUP.csv"
data = read_csv(csv_file)

if data.empty:
    raise ValueError(f"CSV-файл пуст: {csv_file}")


def get_angles(row):
    return [
        row.iloc[1],
        row.iloc[2] - 3.14 / 2,
        row.iloc[3] + 3.14 / 2,
        row.iloc[4],
        row.iloc[5],
        row.iloc[6],
    ]


trajectory = [
    (float(row.iloc[0]), get_angles(row))
    for _, row in data.iterrows()
]

with RukaRobot(config) as robot:
    robot.move_to_angles(trajectory[0][1])
    robot.execute_angle_trajectory(trajectory)
```

Если файл не существует или имеет неверный формат, `read_csv()` не скрывает
ошибку. В сообщении исключения будет указан файл или некорректная строка.

## 9. Скорость и ускорение

Значения по умолчанию:

- максимальная скорость: `0.9`;
- максимальное ускорение: `0.7`.

Их можно задать при создании контроллера:

```python
with RukaRobot(config, max_velocity=0.5, max_acceleration=0.3) as robot:
    robot.move_to_angles([0.0, -1.57, 1.57, 0.0, 0.0, 0.0])
```

Или изменить во время работы:

```python
robot.max_velocity = 0.4
robot.max_acceleration = 0.2
```

Используйте значения в диапазоне, допустимом вашей конфигурацией MoveIt и
контроллерами робота.

## 10. Collision-объекты

### Добавление параллелепипеда

```python
with RukaRobot(config) as robot:
    robot.add_box(
        "box_1",
        position=[0.5, 0.0, 0.5],
        orientation=[0.0, 0.0, 0.0, 1.0],
        size=[0.6, 0.1, 0.01],
    )
```

### Добавление сферы

```python
robot.add_sphere("sphere_1", position=[0.4, 0.0, 0.4], radius=0.1)
```

### Добавление цилиндра или конуса

```python
robot.add_cylinder(
    "cylinder_1",
    position=[0.4, 0.0, 0.4],
    orientation=[0.0, 0.0, 0.0, 1.0],
    height=0.3,
    radius=0.1,
)

robot.add_cone(
    "cone_1",
    position=[0.4, 0.2, 0.4],
    orientation=[0.0, 0.0, 0.0, 1.0],
    height=0.3,
    radius=0.1,
)
```

### Перемещение и удаление

```python
robot.move_collision_object(
    "box_1",
    position=[0.6, 0.0, 0.5],
    orientation=[0.0, 0.0, 0.0, 1.0],
)

robot.remove_collision_object("box_1")
```

ID каждого объекта должен быть уникальным.

После установки библиотеки также доступен интерактивный редактор объектов:

```bash
ruka-collisions \
  --joint-names shoulder_joint upper_arm_joint elbow_joint \
                wrist_1_joint wrist_2_joint wrist_3_joint \
  --base-link base_link \
  --end-effector tool_link \
  --group arm
```

## 11. Конфигурация другого робота

Для другого робота создайте другой объект `RobotConfig`; внутренний код
библиотеки изменять не нужно:

```python
from ruka_py import RobotConfig, RukaRobot

other_config = RobotConfig(
    joint_names=("axis_a", "axis_b", "axis_c", "axis_d"),
    base_link_name="base_link",
    end_effector_name="tool_link",
    group_name="arm",
)

with RukaRobot(other_config, node_name="my_ruka_program") as robot:
    robot.move_to_angles([0, 0, 0, 0])
```

Названия должны точно совпадать с URDF, SRDF и конфигурацией MoveIt, а порядок
суставов — с конфигурацией контроллера.

## 12. Готовые примеры

Примеры находятся в папке `~/ruka_py/examples`:

- `robot_config.py` — имена суставов и звеньев конкретного робота;
- `move_by_angles.py` — движение по углам;
- `move_to_pose.py` — движение по позиции и ориентации;
- `trajectory_from_csv.py` — траектория из CSV;
- `pose_trajectory.py` — траектория позиций и ориентаций.

Например:

```bash
cd ~/ruka_py
python3 examples/move_by_angles.py
```

Перед первым запуском отредактируйте `examples/robot_config.py`. Затем проверьте
значения в примере и убедитесь, что они безопасны для реального робота и
окружающих объектов.

## 13. Типичные ошибки

### `ModuleNotFoundError: No module named 'pymoveit2'`

Подключите ROS workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ws_ruka/install/setup.bash
```

### `ModuleNotFoundError: No module named 'ruka_py'`

Установите библиотеку:

```bash
python3 -m pip install /путь/к/ruka_py
```

### `angles must contain exactly N values`

В точке указано неверное количество углов. Требуется ровно столько чисел,
сколько суставов находится в `config.joint_names`.

### `Trajectory times must be strictly increasing`

Времена точек повторяются или идут в убывающем порядке. Исправьте их так, чтобы
каждое следующее значение было больше предыдущего.

### `MoveIt could not find an IK solution`

Заданная позиция или ориентация недостижима, находится около сингулярности либо
нарушает ограничения. Измените позу и убедитесь, что MoveIt получил актуальное
состояние робота.

### Робот не начинает движение

Проверьте:

1. запущены ли драйверы или симулятор;
2. запущен ли `move_group`;
3. активен ли контроллер манипулятора;
4. публикуется ли `/joint_states`;
5. совпадают ли `group_name`, имена суставов и звеньев с конфигурацией MoveIt;
6. нет ли collision-объекта или ограничения, блокирующего планирование.

## 14. Безопасность

Перед запуском на реальном оборудовании:

1. сначала проверьте сценарий в симуляторе;
2. проверьте единицы измерения: метры, радианы и секунды;
3. используйте небольшие скорость и ускорение при первом запуске;
4. убедитесь, что стартовая конфигурация соответствует первой точке траектории;
5. держите доступной кнопку аварийной остановки;
6. не запускайте непроверенную траекторию рядом с людьми.
