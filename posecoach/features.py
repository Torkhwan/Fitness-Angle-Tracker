"""
features.py  งาน B: เตรียมจุด → features ของแต่ละท่า → เส้นท่าที่ถูก

คำอธิบายงานและสูตร: docs/role_B_vector.md
ทดสอบ: python check.py features
"""
import math

import numpy as np

from vector import J, angle_at, angle_between, cross_z, norm, projection, signed_from_vertical


def prepare_points(ex, pts):
    """ท่า lunge: แยกขาหน้า/ขาหลัง (ขาหน้า = ข้อเท้าที่อยู่ไปทางทิศที่ปลายเท้าชี้)
    ท่าอื่นคืน pts เดิม"""
    raise NotImplementedError("TODO(B)")


def compute_features(ex, Q):
    """Q = จุดหลัง normalize (หันไปทาง +x, y ชี้ขึ้น, สะโพกที่ 0, ลำตัวยาว 1)
    คืน (x, extra)  x = np.array 3 ค่า เรียงตาม EXERCISES[ex]["features"], extra = dict ค่าประกอบ"""
    raise NotImplementedError("TODO(B)")


def ghost_segments(ex, Q, ref):
    """ท่าที่ถูก (พิกัดมาตรฐาน) สำหรับวาดทับ จะถูกแปลงกลับด้วย M⁻¹ ใน analyze
    ref = features ของท่าต้นแบบ correct, คืน list ของ (จุดเริ่ม, จุดปลาย)"""
    raise NotImplementedError("TODO(B)")
