"""
check.py  ทดสอบงานของตัวเองทีละส่วน (เขียนเสร็จแล้ว ไม่ต้องแก้)

  python check.py vector      งาน B  ไม่ต้องรอใคร
  python check.py matrix      งาน A  ไม่ต้องรอใคร*
  python check.py normalize   งาน A  ต้องมี vector.norm ของงาน B
  python check.py angles      งาน B  ไม่ต้องรอใคร

* matrix.py import norm จาก vector.py แต่ชุด matrix ไม่ได้เรียกใช้ จึงรันได้แม้งาน B ยังไม่เสร็จ
"""
import math
import sys

import numpy as np

make_vector = lambda *values: np.array(values, float)
results = []


def check(name, condition):
    results.append(bool(condition))
    print(f"  {'ผ่าน ✔' if condition else 'ไม่ผ่าน ✘'}  {name}")


def check_vector():
    import vector
    check("norm((3,4)) = 5", np.isclose(vector.norm(make_vector(3, 4)), 5))
    check("angle_between((1,0),(0,1)) = 90",
          np.isclose(vector.angle_between(make_vector(1, 0), make_vector(0, 1)), 90))
    check("angle_between((1,0),(2,0)) = 0 (ไม่ error จากการปัดเศษ)",
          np.isclose(vector.angle_between(make_vector(1, 0), make_vector(2, 0)), 0))
    check("angle_at((0,0),(1,0),(-1,0)) = 180",
          np.isclose(vector.angle_at(make_vector(0, 0), make_vector(1, 0), make_vector(-1, 0)), 180))
    component, projected, perpendicular = vector.projection(make_vector(3, 4), make_vector(0, 2))
    check("projection((3,4),(0,2)) = 4, (0,4), (3,0)",
          np.isclose(component, 4) and np.allclose(projected, [0, 4]) and np.allclose(perpendicular, [3, 0]))
    check("cross_z((1,0),(0,1)) = 1, สลับลำดับ = -1",
          np.isclose(vector.cross_z(make_vector(1, 0), make_vector(0, 1)), 1)
          and np.isclose(vector.cross_z(make_vector(0, 1), make_vector(1, 0)), -1))
    check("euclidean((3,4,0),(0,0,0)) = 5",
          np.isclose(vector.euclidean(make_vector(3, 4, 0), make_vector(0, 0, 0)), 5))
    check("manhattan((3,-4,1),(0,0,0)) = 8",
          np.isclose(vector.manhattan(make_vector(3, -4, 1), make_vector(0, 0, 0)), 8))
    check("cosine((1,2,3),(2,4,6)) = 1", np.isclose(vector.cosine(make_vector(1, 2, 3), make_vector(2, 4, 6)), 1))
    check("signed_from_vertical((1,1)) = 45, ((-1,1)) = -45",
          np.isclose(vector.signed_from_vertical(make_vector(1, 1)), 45)
          and np.isclose(vector.signed_from_vertical(make_vector(-1, 1)), -45))


def check_matrix():
    import matrix
    check("apply(translation(2,3), (1,1)) = (3,4)",
          np.allclose(matrix.apply(matrix.translation(2, 3), make_vector(1, 1)), [3, 4]))
    check("apply(rotation(0,1), (1,0)) = (0,1)  หมุนทวนเข็ม 90°",
          np.allclose(matrix.apply(matrix.rotation(0, 1), make_vector(1, 0)), [0, 1]))
    check("apply(scaling(2), (1,3)) = (2,6)", np.allclose(matrix.apply(matrix.scaling(2), make_vector(1, 3)), [2, 6]))
    check("apply(reflect_x(), (1,3)) = (-1,3)", np.allclose(matrix.apply(matrix.reflect_x(), make_vector(1, 3)), [-1, 3]))
    check("apply(reflect_y(), (1,3)) = (1,-3)", np.allclose(matrix.apply(matrix.reflect_y(), make_vector(1, 3)), [1, -3]))
    check("ทุกเมทริกซ์เป็น 3×3 ชนิด float",
          all(made.shape == (3, 3) and made.dtype == float for made in
              (matrix.translation(1, 2), matrix.rotation(1, 0), matrix.scaling(2), matrix.reflect_x(),
               matrix.reflect_y())))
    random_generator = np.random.default_rng(1)
    random_matrix = random_generator.random((3, 3))
    check("determinant_3x3 ตรงกับ np.linalg.det",
          np.isclose(matrix.determinant_3x3(random_matrix), np.linalg.det(random_matrix)))
    check("gauss_jordan_inverse ตรงกับ np.linalg.inv",
          np.allclose(matrix.gauss_jordan_inverse(random_matrix), np.linalg.inv(random_matrix)))
    zero_pivot_matrix = make_vector([0, 1, 2], [1, 0, 3], [4, -3, 8])   # ตำแหน่ง (0,0) เป็น 0 → ต้องสลับแถว
    check("gauss_jordan_inverse เมื่อ pivot แรกเป็น 0 (ต้องสลับแถว)",
          np.allclose(zero_pivot_matrix @ matrix.gauss_jordan_inverse(zero_pivot_matrix), np.eye(3)))
    try:
        matrix.gauss_jordan_inverse(make_vector([1, 2, 3], [2, 4, 6], [1, 0, 1]))
        check("เมทริกซ์เอกฐาน → raise ValueError", False)
    except ValueError:
        check("เมทริกซ์เอกฐาน → raise ValueError", True)


def check_normalize():
    import matrix
    flipped_points = {"shoulder_point": make_vector(47, 54), "hip_point": make_vector(40, 30),
                      "knee_point": make_vector(56, 42), "ankle_point": make_vector(60, 20),
                      "heel_point": make_vector(59, 13), "toe_point": make_vector(71, 22)}
    check("floor_vector squat = (12, 9)", np.allclose(matrix.floor_vector("squat", flipped_points), [12, 9]))
    normalization_matrix, info = matrix.build_normalization_matrix("squat", flipped_points)
    check("normalization_matrix ตรงกับตัวอย่างในข้อเสนอโครงงาน",
          np.allclose(normalization_matrix, [[0.032, 0.024, -2], [-0.024, 0.032, 0], [0, 0, 1]]))
    check("info: cos 0.8, sin 0.6, theta 36.87, torso 25",
          np.allclose([info["cos"], info["sin"], info["theta"], info["torso"]], [0.8, 0.6, 36.8699, 25], atol=1e-3))
    check("info มี key ครบ",
          set(info) == {"translation_matrix", "facing_reflection_matrix", "rotation_matrix", "scaling_matrix",
                        "floor", "cos", "sin", "theta", "torso"})
    check("สะโพก → (0,0), ไหล่ → (0.8,0.6)",
          np.allclose(matrix.apply(normalization_matrix, flipped_points["hip_point"]), [0, 0])
          and np.allclose(matrix.apply(normalization_matrix, flipped_points["shoulder_point"]), [0.8, 0.6]))
    check("determinant_3x3(normalization_matrix) = 1/25² = 0.0016",
          np.isclose(matrix.determinant_3x3(normalization_matrix), 0.0016))
    check("inverse = [[20,-15,40],[15,20,30],[0,0,1]]",
          np.allclose(matrix.gauss_jordan_inverse(normalization_matrix), [[20, -15, 40], [15, 20, 30], [0, 0, 1]]))
    # คนเดิมแต่หันซ้าย
    mirrored_points = {point_name: make_vector(-point[0], point[1]) for point_name, point in flipped_points.items()}
    mirrored_matrix, mirrored_info = matrix.build_normalization_matrix("squat", mirrored_points)
    check("หันซ้าย → ใช้ Fx และได้จุดหลัง normalize เท่าเดิม",
          mirrored_info["facing_reflection_matrix"][0, 0] == -1
          and all(np.allclose(matrix.apply(mirrored_matrix, mirrored_points[point_name]),
                              matrix.apply(normalization_matrix, flipped_points[point_name]))
                  for point_name in flipped_points))


def check_angles():
    import angles
    normalized_points = {"shoulder_point": make_vector(0.8, 0.6), "hip_point": make_vector(0, 0),
                         "knee_point": make_vector(0.8, 0), "ankle_point": make_vector(0.4, -0.8),
                         "heel_point": make_vector(0.2, -1.0), "toe_point": make_vector(0.8, -1.0)}
    angle_values, extra = angles.compute_angles("squat", normalized_points)
    check("squat = [63.43, 36.87, 53.13]", np.allclose(angle_values, [63.4349, 36.8699, 53.1301], atol=1e-3))
    normalized_points = {"shoulder_point": make_vector(1, 0), "elbow_point": make_vector(0.7, -0.3),
                         "wrist_point": make_vector(1, -0.6), "hip_point": make_vector(0, 0),
                         "knee_point": make_vector(-0.8, 0), "ankle_point": make_vector(-1.5, 0),
                         "toe_point": make_vector(-1.6, -0.6)}
    angle_values, _ = angles.compute_angles("pushup", normalized_points)
    check("pushup ลำตัวตรง = [90, 0, 0]", np.allclose(angle_values, [90, 0, 0], atol=1e-6))
    angle_values, _ = angles.compute_angles("pushup", {**normalized_points, "hip_point": make_vector(0, -0.25)})
    check("pushup สะโพกตก → hip_deviation ติดลบ", angle_values[1] < -10)
    angle_values, _ = angles.compute_angles("pushup", {**normalized_points, "hip_point": make_vector(0, 0.25)})
    check("pushup สะโพกโด่ง → hip_deviation เป็นบวก", angle_values[1] > 10)
    raw_points = {"shoulder_point": make_vector(0, 1), "hip_point": make_vector(0, 0),
                  "left_knee_point": make_vector(0.9, 0), "left_ankle_point": make_vector(0.9, -0.9),
                  "left_heel_point": make_vector(0.8, -1.0), "left_toe_point": make_vector(1.1, -1.0),
                  "right_knee_point": make_vector(-0.45, -0.8), "right_ankle_point": make_vector(-1.2, -0.75),
                  "right_heel_point": make_vector(-1.3, -0.8), "right_toe_point": make_vector(-1.05, -1.0)}
    lunge_points = angles.prepare_points("lunge", raw_points)
    check("prepare_points lunge: key ครบ 10 ตัว (shoulder, hip, front_…, back_…), ขาหน้า = ซ้าย",
          set(lunge_points) == {"shoulder_point", "hip_point", "front_knee_point", "front_ankle_point",
                                "front_heel_point", "front_toe_point", "back_knee_point", "back_ankle_point",
                                "back_heel_point", "back_toe_point"}
          and np.allclose(lunge_points["front_knee_point"], raw_points["left_knee_point"]))
    mirrored_points = {point_name: make_vector(-point[0], point[1]) for point_name, point in raw_points.items()}
    check("prepare_points lunge: หันซ้ายก็ยังเลือกขาหน้าถูก",
          np.allclose(angles.prepare_points("lunge", mirrored_points)["front_knee_point"],
                      mirrored_points["left_knee_point"]))
    check("prepare_points ท่าอื่นคืนค่าเดิม", angles.prepare_points("squat", normalized_points) is normalized_points)
    angle_values, _ = angles.compute_angles("lunge", lunge_points)
    check("lunge = [90, 0, 0]", np.allclose(angle_values, [90, 0, 0], atol=1e-6))
    segments = angles.ghost_segments("squat", {"hip_point": make_vector(0, 0)}, make_vector(65, 55, 30))
    check("ghost squat: เส้นจากสะโพกไป (sin30°, cos30°)",
          len(segments) == 1 and np.allclose(segments[0][1], [0.5, math.sqrt(3) / 2]))
    segments = angles.ghost_segments("pushup", {**normalized_points, "hip_point": make_vector(0, -0.25)},
                                     make_vector(90, 0, 5))
    check("ghost pushup: สะโพกที่ถูกอยู่บนเส้นไหล่-ข้อเท้า", len(segments) == 2 and np.allclose(segments[0][1], [0, 0]))
    segments = angles.ghost_segments("lunge", lunge_points, make_vector(90, 0, 0))
    check("ghost lunge: เส้นหน้าแข้งยาวเท่าหน้าแข้งจริง ปลายอยู่ที่เข่าหน้า",
          len(segments) == 2 and np.allclose(segments[0][1], lunge_points["front_knee_point"]))


if __name__ == "__main__":
    test_sets = {"vector": check_vector, "matrix": check_matrix, "normalize": check_normalize, "angles": check_angles}
    if len(sys.argv) != 2 or sys.argv[1] not in test_sets:
        sys.exit("ใช้: python check.py " + " | ".join(test_sets))
    try:
        test_sets[sys.argv[1]]()
    except NotImplementedError as error:
        sys.exit(f"ยังมีฟังก์ชันที่ไม่ได้เขียน: {error}")
    print(f"\n{sys.argv[1]}: ผ่าน {sum(results)}/{len(results)}")
    sys.exit(0 if all(results) else 1)
