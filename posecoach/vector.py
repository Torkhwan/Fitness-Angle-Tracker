"""
vector.py  งาน B: เวกเตอร์ (บท 1-2)

คำอธิบายงานและสูตร: docs/vector_angles.md
ทดสอบ: python check.py vector
ไฟล์นี้ต้องไม่ import ไฟล์อื่นของโครงงาน (ทุกคนเรียกใช้ไฟล์นี้)
"""
import math

import numpy as np

# เวกเตอร์หนึ่งหน่วยแนวตั้ง ĵ = (0, 1) ใช้วัดว่าเวกเตอร์เอียงจากแนวตั้งกี่องศา
vertical_unit_vector = np.array([0.0, 1.0])


def norm(vector):
    """|vector| จาก dot product (ห้ามใช้ np.linalg.norm)"""
    return float(math.sqrt(np.dot(vector,vector)))


def angle_between(first_vector, second_vector):
    """มุมระหว่างเวกเตอร์สองตัว (องศา 0-180) จาก dot product"""
    cosine_value=(np.dot(first_vector,second_vector))/(norm(first_vector)*norm(second_vector))
    return float(math.degrees(math.acos(max(-1.0,min(1.0,(cosine_value))))))


def angle_at(center_point, first_point, second_point):
    """มุมที่ข้อต่อ center_point ด้วย dot product (เวกเตอร์เริ่มจากข้อต่อเสมอ)"""
    first_vector=first_point-center_point
    second_vector=second_point-center_point
    return angle_between(first_vector,second_vector)


def projection(vector, base_vector):
    """ฉาย vector ลงบน base_vector คืน (component, projected, perpendicular)
    component = ความยาวของเงา (comp), projected = เวกเตอร์เงา (proj), perpendicular = ส่วนตั้งฉาก"""
    component=np.dot(vector,base_vector)/norm(base_vector)
    projected=(np.dot(vector,base_vector)/np.dot(base_vector,base_vector))*base_vector
    perpendicular=vector-projected
    return component,projected,perpendicular


def cross_z(first_vector, second_vector):
    """องค์ประกอบ z ของ first_vector × second_vector (เวกเตอร์ 2 มิติ)"""
    return float((first_vector[0]*second_vector[1])-(first_vector[1]*second_vector[0]))


def euclidean(first_vector, second_vector):
    return norm(first_vector - second_vector)


def manhattan(first_vector, second_vector):
    return float(np.sum(np.abs(first_vector - second_vector)))


def cosine(first_vector, second_vector):
    """cosine similarity"""
    cosine_value=(np.dot(first_vector,second_vector))/(norm(first_vector)*norm(second_vector))
    return float((max(-1.0, min(1.0, cosine_value))))


def signed_from_vertical(vector):
    """มุมของ vector จากแนวตั้ง (องศา) บวก = เอียงไปข้างหน้า (+x) ใช้ projection บน ĵ"""
    component, _, perpendicular = projection(vector, vertical_unit_vector)
    cosine_value = component / norm(vector)
    angle = math.degrees(math.acos(max(-1.0, min(1.0, cosine_value))))
    return float(angle if perpendicular[0] >= 0 else -angle)
