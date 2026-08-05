"""Движение по траектории углов из CSV."""

from pathlib import Path

from ruka_py import RukaRobot, read_csv

csv_file = Path.home() / "Desktop" / "data_csv_ruka_fk" / "UDRIVEUP.csv"
angles = read_csv(csv_file)
if angles.empty:
    raise ValueError(f"CSV-файл не содержит точек: {csv_file}")


def joint_angles(row):
    return [
        row.iloc[1],
        row.iloc[2] - 3.14 / 2,
        row.iloc[3] + 3.14 / 2,
        row.iloc[4],
        row.iloc[5],
        row.iloc[6],
    ]


first_joint_goal = joint_angles(angles.iloc[0])
trajectory = [(row.iloc[0], joint_angles(row)) for _, row in angles.iterrows()]

with RukaRobot() as robot:
    robot.move_to_angles(first_joint_goal)
    robot.execute_angle_trajectory(trajectory)
