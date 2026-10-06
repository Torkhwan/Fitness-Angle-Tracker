"""
vector.py  งาน B: เวกเตอร์ (บท 1-2)

คำอธิบายงานและสูตร: docs/role_B_vector.md
ทดสอบ: python check.py vector
ไฟล์นี้ต้องไม่ import ไฟล์อื่นของโครงงาน (ทุกคนเรียกใช้ไฟล์นี้)
"""
import math

import numpy as np

J = np.array([0.0, 1.0])


def norm(v):
    """|v| จาก dot product (ห้ามใช้ np.linalg.norm)"""
    return float(math.sqrt(np.dot(v,v)))


def angle_between(u, v):
    """มุมระหว่าง u กับ v (องศา 0-180) จาก dot product"""
    c=(np.dot(u,v))/(norm(u)*norm(v))
    return float(math.degrees(math.acos(max(-1.0,min(1.0,(c))))))


def angle_at(center, p1, p2):
    """มุมที่ข้อต่อ center ด้วย dot product (เวกเตอร์เริ่มจากข้อต่อเสมอ)"""
    u=p1-center
    v=p2-center
    return angle_between(u,v)


def projection(t, b):
    """คืน (comp_b t, proj_b t, ส่วนตั้งฉาก)"""
    comp=np.dot(t,b)/norm(b)
    proj=(np.dot(t,b)/np.dot(b,b))*b
    perp=t-proj
    return comp,proj,perp


def cross_z(u, v):
    """องค์ประกอบ z ของ u × v (เวกเตอร์ 2 มิติ)"""
    return float((u[0]*v[1])-(u[1]*v[0]))


def euclidean(a, b):
    return norm(a - b)


def manhattan(a, b):
    return float(np.sum(np.abs(a - b)))


def cosine(a, b):
    """cosine similarity"""
    c=(np.dot(a,b))/(norm(a)*norm(b))
    return float((max(-1.0, min(1.0, c))))


def signed_from_vertical(v):
    """มุมของ v จากแนวตั้ง (องศา) บวก = เอียงไปข้างหน้า (+x) ใช้ projection บน ĵ"""
    comp, _, perp = projection(v, J)
    c = comp / norm(v)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, c))))
    return float(ang if perp[0] >= 0 else -ang)
