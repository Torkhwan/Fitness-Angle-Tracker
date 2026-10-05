"""
matrix.py  งาน A: เมทริกซ์และการ normalize (บท 4, 5, 7, 8, 9)

คำอธิบายงานและสูตร: docs/role_A_matrix.md
ทดสอบ: python check.py matrix   และ   python check.py normalize
"""
import math

import numpy as np

from config import EXERCISES
from vector import norm


#
# 1) เมทริกซ์การแปลง 3×3 (homogeneous coordinates)
#
def translation(tx, ty):
    """T(tx, ty) เลื่อนจุด"""
    return np.array([[1, 0, tx],
                     [0, 1, ty],
                     [0, 0, 1]
                    ], dtype=float)

def rotation(cos_t, sin_t):
    """R(θ) หมุนทวนเข็ม รับ cos θ, sin θ  (ส่ง sin เป็นลบเพื่อได้ R(−θ))"""
    return np.array([[cos_t, -sin_t, 0],
                     [sin_t, cos_t, 0],
                     [0, 0, 1]
                    ], dtype=float)

def scaling(s):
    """S(s) ย่อขยายเท่ากันทั้งสองแกน"""
    return np.array([[s, 0, 0],
                     [0, s, 0],
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

def det3(M):
    """det ของเมทริกซ์ 3×3 ด้วย cofactor expansion ตามแถวแรก (ห้ามใช้ np.linalg.det)"""
    a, b, c = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def gauss_jordan_inverse(M):
    """[M | I] → [I | M⁻¹] ด้วย Gauss-Jordan elimination (ห้ามใช้ np.linalg.inv)
    ถ้า pivot เป็น 0 ให้ raise ValueError("Singular matrix (det = 0)")"""
    n = M.shape[0]
    aug = np.hstack([M.astype(float), np.eye(n)])
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r, col]))
        if abs(aug[pivot, col]) < 1e-12:
            raise ValueError("Singular matrix (det = 0)")
        # สลับแถว
        aug[[col, pivot]] = aug[[pivot, col]]
        # ปรับแนวทแยงเป็น 1
        aug[col] /= aug[col, col]
        # ทำให้ตำแหน่งอื่นเป็น 0
        for r in range(n):
            if r != col:
                aug[r] -= aug[r, col] * aug[col]
    return aug[:, n:]


def apply(M, p):
    """p' = M · p  รับจุด 2 มิติ คืนจุด 2 มิติ (เติม 1 เป็น homogeneous ข้างใน)"""
    return (M @ np.array([p[0], p[1], 1.0]))[:2]


#
# 2) Normalize: M = S · R(−θ) · [Fx] · T
#
def floor_vector(ex, P):
    """เวกเตอร์แนวพื้นที่ชี้ไปทางหน้าของผู้ใช้
    squat: ส้นเท้า → ปลายเท้า, pushup: ปลายเท้า → ข้อมือ, lunge: ส้นเท้าหน้า → ปลายเท้าหน้า"""
    if ex == "squat":
        return P["TO"] - P["HL"]            
    if ex == "pushup":
        return P["W"] - P["TO"] 
    return P["TOf"] - P["HLf"]

def normalization_matrix(ex, P):
    """คืน (M, info)
    info = {"T", "F", "R", "S", "floor", "cos", "sin", "theta", "torso"}  (ดู docs/shared_structure.md)"""
    # 1. Translation (ย้ายสะโพกไป (0,0))
    T = translation(-P["H"][0], -P["H"][1])
    # 2. Reflection (พลิกให้หันขวา)
    f = floor_vector(ex, P)
    F = reflect_x() if f[0] < 0 else np.eye(3)
    f2 = F[:2, :2] @ f
    # 3. Rotation (หมุนพื้นขนานแกน x)
    c, s = f2[0] / norm(f2), f2[1] / norm(f2)
    R = rotation(c, -s)
    # 4. Scaling (ปรับลำตัวยาว 1)
    torso = norm(P["S"] - P["H"])
    S = scaling(1.0 / torso)
    
    M = S @ R @ F @ T
    return M, {"T": T, "F": F, "R": R, "S": S, "floor": f, "cos": c, "sin": s,
               "theta": math.degrees(math.atan2(s, c)), "torso": torso}

#
# 3) พิมพ์ขั้นตอนคำนวณ (--explain)
#
def fmt(v):
    """จัดรูปตัวเลข: เวกเตอร์ → "(0.8000, 0.6000)", ตัวเลขเดี่ยว → "0.8000" """
    if isinstance(v, np.ndarray):
        return "(" + ", ".join(f"{c:.4f}" for c in v) + ")"
    return f"{v:.4f}"

def print_explain(pts_img, r):
    """พิมพ์การคำนวณทีละขั้นจาก result dict r (หัวข้อ 1-6 ตาม docs/role_A_matrix.md)"""
    np.set_printoptions(precision=4, suppress=True)
    ex, i, cfg = r["ex"], r["info"], EXERCISES[r["ex"]]
    print(f"\n================ คำอธิบายการคำนวณ: {cfg['th']} ================")
    
    print("1) พิกัดภาพ → กลับแกน y ด้วย Fy = diag(1, −1, 1)")
    for k, v in r["P"].items():
        print(f"   {k:>3} = ({v[0]:.2f}, {v[1]:.2f})")
    
    print(f"2) เวกเตอร์แนวพื้น f = {fmt(i['floor'])}, |f| = {norm(i['floor']):.4f}"
          + ("  → ชี้ซ้าย จึงสะท้อน x ด้วย Fx ก่อน" if i["F"][0, 0] < 0 else ""))
    print(f"   f̂ = (cos θ, sin θ) = ({i['cos']:.4f}, {i['sin']:.4f}), θ = {i['theta']:.2f}°")
    
    print(f"3) ความยาวลำตัว |S − H| = {i['torso']:.4f}")
    print("   T =\n", i["T"])
    if i["F"][0, 0] < 0:
        print("   Fx =\n", i["F"])
    print("   R(−θ) =\n", i["R"])
    print("   S =\n", i["S"])
    print("   M = S·R(−θ)·[Fx]·T =\n", r["M"])
    print(f"   det(M) = {det3(r['M']):.8f}  (≠ 0 → หา inverse ได้)")
    print("   M⁻¹ (Gauss-Jordan) =\n", r["M_inv"])
    print("   ตรวจ M·M⁻¹ = I :", np.allclose(r["M"] @ r["M_inv"], np.eye(3)))
    
    print("4) จุดหลัง normalize (p' = M·p):")
    for k, v in r["Q"].items():
        print(f"   {k:>3}' = {fmt(v)}")
    
    print("5) Features:")
    for (name, th, _, _), val in zip(cfg["features"], r["x"]):
        print(f"   {th:<28} = {val:8.2f}°")
    for k, v in r["extra"].items():
        print(f"   {k:<28} = {fmt(v)}")
    
    print("6) เทียบท่าต้นแบบ" + ("" if r["from_file"] else " (ค่าสมมติ)") + ":")
    for row in r["ranking"]:
        print(f"   {cfg['labels'].get(row['name'], row['name']):<30} Euclid={row['euclid']:7.2f}  "
              f"Manhattan={row['manhattan']:7.2f}  Cosine={row['cosine']:.4f}")
    print("=" * 60 + "\n")