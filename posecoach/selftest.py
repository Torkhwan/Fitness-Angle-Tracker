"""
selftest.py  ทดสอบรวมทั้งระบบ (เขียนเสร็จแล้ว ไม่ต้องแก้)

  python selftest.py

ต้องผ่านทุกข้อก่อนเริ่มเก็บข้อมูล ใช้ได้เมื่องาน A, B, C merge เข้า main ครบแล้ว
"""
import math
import sys

import numpy as np

from analyze import analyze, print_result
from angles import prepare_points
from config import EXERCISES
from matrix import (apply, determinant_3x3, gauss_jordan_inverse, reflect_x, reflect_y, rotation, scaling,
                    translation)


def random_view(points, random_generator):
    """จำลองการถ่ายภาพ: หมุนกล้อง ±25°, ย่อขยาย, เลื่อน, (อาจ) หันซ้าย แล้วเป็นพิกัดภาพ y ชี้ลง"""
    angle = math.radians(random_generator.uniform(-25, 25))
    scale_factor = random_generator.uniform(50, 300)
    mirror = random_generator.random() < 0.5
    camera_matrix = (translation(random_generator.uniform(300, 600), random_generator.uniform(300, 600))
                     @ reflect_y() @ scaling(scale_factor) @ rotation(math.cos(angle), math.sin(angle))
                     @ (reflect_x() if mirror else np.eye(3)))
    return {point_name: apply(camera_matrix, np.array(point, float)) for point_name, point in points.items()}


def selftest():
    all_passed = True
    fixed_templates = lambda exercise: {label: np.array(values, float)
                                        for label, values in EXERCISES[exercise]["templates"].items()}

    # (ก) ตัวอย่างในข้อเสนอโครงงาน — ตัวเลขต้องตรง
    example_points = {"shoulder_point": (47, 54), "hip_point": (40, 30), "knee_point": (56, 42),
                      "ankle_point": (60, 20), "heel_point": (59, 13), "toe_point": (71, 22)}
    result = analyze("squat", {point_name: np.array([point[0], -point[1]], float)
                               for point_name, point in example_points.items()},
                     explain=True, templates=fixed_templates("squat"))
    passed = (np.allclose(result["angle_values"], [63.4349, 36.8699, 53.1301], atol=1e-3)
              and np.allclose(result["normalization_matrix"], [[0.032, 0.024, -2], [-0.024, 0.032, 0], [0, 0, 1]])
              and np.allclose(result["inverse_matrix"], [[20, -15, 40], [15, 20, 30], [0, 0, 1]])
              and result["ranking"][0]["name"] == "lean_forward"
              and abs(result["ranking"][0]["euclidean"] - 3.07) < 0.01)
    print_result(result)
    print("  (ก) ตัวอย่างในข้อเสนอโครงงาน:", "ผ่าน ✔" if passed else "ไม่ผ่าน ✘")
    all_passed &= passed

    # (ข) ท่าที่สร้างขึ้นซึ่งรู้คำตอบ + ถ่ายจากมุมสุ่ม 50 ครั้ง ต้องได้มุมเท่าเดิม
    cases = {
        "pushup": ({"shoulder_point": (1, 0), "elbow_point": (0.7, -0.3), "wrist_point": (1, -0.6),
                    "hip_point": (0, 0), "knee_point": (-0.8, 0), "ankle_point": (-1.5, 0),
                    "toe_point": (-1.6, -0.6)}, [90, 0, 0], "correct"),
        "lunge": ({"shoulder_point": (0, 1), "hip_point": (0, 0),
                   "left_knee_point": (0.9, 0), "left_ankle_point": (0.9, -0.9),
                   "left_heel_point": (0.8, -1.0), "left_toe_point": (1.1, -1.0),
                   "right_knee_point": (-0.45, -0.8), "right_ankle_point": (-1.2, -0.75),
                   "right_heel_point": (-1.3, -0.8), "right_toe_point": (-1.05, -1.0)}, [90, 0, 0], "correct"),
    }
    sagging_pose = dict(cases["pushup"][0])
    sagging_pose["hip_point"] = (0, -0.25)
    random_generator = np.random.default_rng(7)
    for exercise, (pose, expected_values, expected_label) in cases.items():
        passed = True
        for _ in range(50):
            points = prepare_points(exercise, random_view(pose, random_generator))
            result = analyze(exercise, points, templates=fixed_templates(exercise))
            passed &= (np.allclose(result["angle_values"], expected_values, atol=1e-6)
                       and result["ranking"][0]["name"] == expected_label)
            passed &= np.allclose(result["normalization_matrix"] @ result["inverse_matrix"], np.eye(3))
        print(f"  (ข) {EXERCISES[exercise]['thai_name']}: มุม {np.round(result['angle_values'], 2)} คงที่ทุกมุมกล้อง →",
              "ผ่าน ✔" if passed else "ไม่ผ่าน ✘")
        all_passed &= passed
    result = analyze("pushup", random_view(sagging_pose, random_generator), templates=fixed_templates("pushup"))
    passed = result["angle_values"][1] < -10 and result["ranking"][0]["name"] == "hip_sag"
    print(f"  (ค) วิดพื้นสะโพกตก: hip_deviation = {result['angle_values'][1]:.2f}° → {result['ranking'][0]['name']} →",
          "ผ่าน ✔" if passed else "ไม่ผ่าน ✘")
    all_passed &= passed
    random_matrix = random_generator.random((3, 3))
    passed = (np.allclose(gauss_jordan_inverse(random_matrix), np.linalg.inv(random_matrix))
              and np.isclose(determinant_3x3(random_matrix), np.linalg.det(random_matrix)))
    print("  (ง) Gauss-Jordan / determinant_3x3 เทียบกับ NumPy:", "ผ่าน ✔" if passed else "ไม่ผ่าน ✘")
    all_passed &= passed
    print("\nSELFTEST:", "ผ่านทั้งหมด ✔" if all_passed else "มีข้อไม่ผ่าน ✘")
    return all_passed


if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)
