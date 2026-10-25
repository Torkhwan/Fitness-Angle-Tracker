"""
matrix.py  งาน A: เมทริกซ์และการ normalize (บท 4, 5, 7, 8, 9)

คำอธิบายงานและสูตร: docs/matrix.md
ทดสอบ: python check.py matrix   และ   python check.py normalize
"""
import math

import numpy as np

from config import EXERCISES
from vector import norm


#
# 1) เมทริกซ์การแปลง 3×3 (homogeneous coordinates)
#
def translation(shift_x, shift_y):
    """T เลื่อนจุดไป shift_x, shift_y"""
    return np.array([[1, 0, shift_x],
                     [0, 1, shift_y],
                     [0, 0, 1]
                    ], dtype=float)

def rotation(cos_theta, sin_theta):
    """R(θ) หมุนทวนเข็ม รับ cos θ, sin θ  (ส่ง sin เป็นลบเพื่อได้ R(−θ))"""
    return np.array([[cos_theta, -sin_theta, 0],
                     [sin_theta, cos_theta, 0],
                     [0, 0, 1]
                    ], dtype=float)

def scaling(scale_factor):
    """S ย่อขยายเท่ากันทั้งสองแกน"""
    return np.array([[scale_factor, 0, 0],
                     [0, scale_factor, 0],
                     [0, 0, 1]
                    ], dtype=float)

def reflect_x():
    """Fx กลับเครื่องหมาย x (สะท้อนซ้าย-ขวา)"""
    return np.array([[-1, 0, 0],
                     [0, 1, 0],
                     [0, 0, 1]
                    ], dtype=float)

def reflect_y():
    """Fy กลับเครื่องหมาย y (สะท้อนบน-ล่าง)"""
    return np.array([[1, 0, 0],
                     [0, -1, 0],
                     [0, 0, 1]
                    ], dtype=float)

def determinant_3x3(matrix):
    """det ของเมทริกซ์ 3×3 ด้วย cofactor expansion ตามแถวแรก (ห้ามใช้ np.linalg.det)"""
    # a ถึง i คือสมาชิกของเมทริกซ์ตามสูตร   [[a, b, c],
    #                                       [d, e, f],
    #                                       [g, h, i]]
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def gauss_jordan_inverse(matrix):
    """[M | I] → [I | M⁻¹] ด้วย Gauss-Jordan elimination (ห้ามใช้ np.linalg.inv)
    ถ้า pivot เป็น 0 ให้ raise ValueError("Singular matrix (det = 0)")"""
    size = matrix.shape[0]
    augmented = np.hstack([matrix.astype(float), np.eye(size)])
    for column in range(size):
        pivot_row = max(range(column, size), key=lambda row: abs(augmented[row, column]))
        if abs(augmented[pivot_row, column]) < 1e-12:
            raise ValueError("Singular matrix (det = 0)")
        # สลับแถว
        augmented[[column, pivot_row]] = augmented[[pivot_row, column]]
        # ปรับแนวทแยงเป็น 1
        augmented[column] /= augmented[column, column]
        # ทำให้ตำแหน่งอื่นเป็น 0
        for row in range(size):
            if row != column:
                augmented[row] -= augmented[row, column] * augmented[column]
    return augmented[:, size:]


def apply(matrix, point):
    """point' = matrix · point  รับจุด 2 มิติ คืนจุด 2 มิติ (เติม 1 เป็น homogeneous ข้างใน)"""
    return (matrix @ np.array([point[0], point[1], 1.0]))[:2]


#
# 2) Normalize: M = S · R(−θ) · [Fx] · T
#
def floor_vector(exercise, flipped_points):
    """เวกเตอร์แนวพื้นที่ชี้ไปทางหน้าของผู้ใช้
    squat: ส้นเท้า → ปลายเท้า, pushup: ปลายเท้า → ข้อมือ, lunge: ส้นเท้าหน้า → ปลายเท้าหน้า"""
    if exercise == "squat":
        return flipped_points["toe_point"] - flipped_points["heel_point"]
    if exercise == "pushup":
        return flipped_points["wrist_point"] - flipped_points["toe_point"]
    return flipped_points["front_toe_point"] - flipped_points["front_heel_point"]

def build_normalization_matrix(exercise, flipped_points):
    """คืน (normalization_matrix, info)
    info = {"translation_matrix", "facing_reflection_matrix", "rotation_matrix", "scaling_matrix",
            "floor", "cos", "sin", "theta", "torso"}  (ดู docs/data_structure.md)"""
    # 1. Translation (ย้ายสะโพกไป (0,0))
    translation_matrix = translation(-flipped_points["hip_point"][0], -flipped_points["hip_point"][1])
    # 2. Reflection (พลิกให้หันขวา)
    floor = floor_vector(exercise, flipped_points)
    facing_reflection_matrix = reflect_x() if floor[0] < 0 else np.eye(3)
    reflected_floor = facing_reflection_matrix[:2, :2] @ floor
    # 3. Rotation (หมุนพื้นขนานแกน x)
    cos_theta, sin_theta = reflected_floor[0] / norm(reflected_floor), reflected_floor[1] / norm(reflected_floor)
    rotation_matrix = rotation(cos_theta, -sin_theta)
    # 4. Scaling (ปรับลำตัวยาว 1)
    torso_length = norm(flipped_points["shoulder_point"] - flipped_points["hip_point"])
    scaling_matrix = scaling(1.0 / torso_length)

    # M = S · R(−θ) · [Fx] · T
    normalization_matrix = scaling_matrix @ rotation_matrix @ facing_reflection_matrix @ translation_matrix
    return normalization_matrix, {"translation_matrix": translation_matrix,
                                  "facing_reflection_matrix": facing_reflection_matrix,
                                  "rotation_matrix": rotation_matrix, "scaling_matrix": scaling_matrix,
                                  "floor": floor, "cos": cos_theta, "sin": sin_theta,
                                  "theta": math.degrees(math.atan2(sin_theta, cos_theta)), "torso": torso_length}

#
# 3) พิมพ์ขั้นตอนคำนวณ (--explain)
#
def format_number(value):
    """จัดรูปตัวเลข: เวกเตอร์ → "(0.8000, 0.6000)", ตัวเลขเดี่ยว → "0.8000" """
    if isinstance(value, np.ndarray):
        return "(" + ", ".join(f"{coordinate:.4f}" for coordinate in value) + ")"
    return f"{value:.4f}"

def print_explain(image_points, result):
    """พิมพ์การคำนวณทีละขั้นจาก result (หัวข้อ 1-6 ตาม docs/matrix.md)"""
    np.set_printoptions(precision=4, suppress=True)
    exercise, info, exercise_config = result["exercise"], result["info"], EXERCISES[result["exercise"]]
    print(f"\n================ คำอธิบายการคำนวณ: {exercise_config['thai_name']} ================")

    print("1) พิกัดภาพ → กลับแกน y ด้วย Fy = diag(1, −1, 1)")
    for point_name, point in result["flipped_points"].items():
        print(f"   {point_name:>18} = ({point[0]:.2f}, {point[1]:.2f})")

    print(f"2) เวกเตอร์แนวพื้น f = {format_number(info['floor'])}, |f| = {norm(info['floor']):.4f}"
          + ("  → ชี้ซ้าย จึงสะท้อน x ด้วย Fx ก่อน" if info["facing_reflection_matrix"][0, 0] < 0 else ""))
    print(f"   f̂ = (cos θ, sin θ) = ({info['cos']:.4f}, {info['sin']:.4f}), θ = {info['theta']:.2f}°")

    print(f"3) ความยาวลำตัว |ไหล่ − สะโพก| = {info['torso']:.4f}")
    print("   T (translation_matrix) =\n", info["translation_matrix"])
    if info["facing_reflection_matrix"][0, 0] < 0:
        print("   Fx (facing_reflection_matrix) =\n", info["facing_reflection_matrix"])
    print("   R(−θ) (rotation_matrix) =\n", info["rotation_matrix"])
    print("   S (scaling_matrix) =\n", info["scaling_matrix"])
    print("   M = S·R(−θ)·[Fx]·T (normalization_matrix) =\n", result["normalization_matrix"])
    print(f"   det(M) = {determinant_3x3(result['normalization_matrix']):.8f}  (≠ 0 → หา inverse ได้)")
    print("   M⁻¹ (inverse_matrix, Gauss-Jordan) =\n", result["inverse_matrix"])
    print("   ตรวจ M·M⁻¹ = I :", np.allclose(result["normalization_matrix"] @ result["inverse_matrix"], np.eye(3)))

    print("4) จุดหลัง normalize (จุดใหม่ = M · จุดเดิม):")
    for point_name, point in result["normalized_points"].items():
        print(f"   {point_name:>18} = {format_number(point)}")

    print("5) มุมของท่า:")
    for (name, thai_name, _, _), value in zip(exercise_config["angles"], result["angle_values"]):
        print(f"   {thai_name:<28} = {value:8.2f}°")
    for extra_name, value in result["extra"].items():
        print(f"   {extra_name:<28} = {format_number(value)}")

    print("6) เทียบท่าต้นแบบ" + ("" if result["from_file"] else " (ค่าสมมติ)") + ":")
    for ranking_row in result["ranking"]:
        print(f"   {exercise_config['labels'].get(ranking_row['name'], ranking_row['name']):<30} "
              f"Euclidean={ranking_row['euclidean']:7.2f}  "
              f"Manhattan={ranking_row['manhattan']:7.2f}  Cosine={ranking_row['cosine']:.4f}")
    print("=" * 60 + "\n")
