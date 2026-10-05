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
        aug[[col, pivot]] = aug[[pivot, col]]
        aug[col] /= aug[col, col]
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
    raise NotImplementedError("TODO(A)")


def normalization_matrix(ex, P):
    """คืน (M, info)
    info = {"T", "F", "R", "S", "floor", "cos", "sin", "theta", "torso"}  (ดู docs/shared_structure.md)"""
    raise NotImplementedError("TODO(A)")


#
# 3) พิมพ์ขั้นตอนคำนวณ (--explain)
#
def fmt(v):
    """จัดรูปตัวเลข: เวกเตอร์ → "(0.8000, 0.6000)", ตัวเลขเดี่ยว → "0.8000" """
    raise NotImplementedError("TODO(A)")


def print_explain(pts_img, r):
    """พิมพ์การคำนวณทีละขั้นจาก result dict r (หัวข้อ 1-6 ตาม docs/role_A_matrix.md)"""
    raise NotImplementedError("TODO(A)")
