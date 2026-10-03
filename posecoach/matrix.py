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
    raise NotImplementedError("TODO(A)")


def rotation(cos_t, sin_t):
    """R(θ) หมุนทวนเข็ม รับ cos θ, sin θ  (ส่ง sin เป็นลบเพื่อได้ R(−θ))"""
    raise NotImplementedError("TODO(A)")


def scaling(s):
    """S(s) ย่อขยายเท่ากันทั้งสองแกน"""
    raise NotImplementedError("TODO(A)")


def reflect_x():
    """Fx กลับเครื่องหมาย x (สะท้อนซ้าย-ขวา)"""
    raise NotImplementedError("TODO(A)")


def reflect_y():
    """Fy กลับเครื่องหมาย y (สะท้อนบน-ล่าง)"""
    raise NotImplementedError("TODO(A)")


def det3(M):
    """det ของเมทริกซ์ 3×3 ด้วย cofactor expansion ตามแถวแรก (ห้ามใช้ np.linalg.det)"""
    raise NotImplementedError("TODO(A)")


def gauss_jordan_inverse(M):
    """[M | I] → [I | M⁻¹] ด้วย Gauss-Jordan elimination (ห้ามใช้ np.linalg.inv)
    ถ้า pivot เป็น 0 ให้ raise ValueError("Singular matrix (det = 0)")"""
    raise NotImplementedError("TODO(A)")


def apply(M, p):
    """p' = M · p  รับจุด 2 มิติ คืนจุด 2 มิติ (เติม 1 เป็น homogeneous ข้างใน)"""
    raise NotImplementedError("TODO(A)")


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
