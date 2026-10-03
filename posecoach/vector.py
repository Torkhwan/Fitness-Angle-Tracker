"""
vector.py  งาน B: เวกเตอร์ (บท 1-2)

คำอธิบายงานและสูตร: docs/role_B_vector.md
ทดสอบ: python check.py vector
ไฟล์นี้ต้องไม่ import ไฟล์อื่นของโครงงาน (ทุกคนเรียกใช้ไฟล์นี้)
"""
import math

import numpy as np

J = np.array([0.0, 1.0])   # เวกเตอร์หนึ่งหน่วยแนวตั้ง


def norm(v):
    """|v| จาก dot product (ห้ามใช้ np.linalg.norm)"""
    raise NotImplementedError("TODO(B)")


def angle_between(u, v):
    """มุมระหว่าง u กับ v (องศา 0-180) จาก dot product"""
    raise NotImplementedError("TODO(B)")


def angle_at(center, p1, p2):
    """มุมที่ข้อต่อ center ด้วย dot product (เวกเตอร์เริ่มจากข้อต่อเสมอ)"""
    raise NotImplementedError("TODO(B)")


def projection(t, b):
    """คืน (comp_b t, proj_b t, ส่วนตั้งฉาก)"""
    raise NotImplementedError("TODO(B)")


def cross_z(u, v):
    """องค์ประกอบ z ของ u × v (เวกเตอร์ 2 มิติ)"""
    raise NotImplementedError("TODO(B)")


def euclidean(a, b):
    raise NotImplementedError("TODO(B)")


def manhattan(a, b):
    raise NotImplementedError("TODO(B)")


def cosine(a, b):
    """cosine similarity"""
    raise NotImplementedError("TODO(B)")


def signed_from_vertical(v):
    """มุมของ v จากแนวตั้ง (องศา) บวก = เอียงไปข้างหน้า (+x) ใช้ projection บน ĵ"""
    raise NotImplementedError("TODO(B)")
