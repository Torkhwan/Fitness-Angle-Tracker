"""
analyze.py  งาน C: เทียบท่าต้นแบบและสรุปผล

คำอธิบายงานและสูตร: docs/role_C_analyze.md
ทดสอบ: python selftest.py  (ต้องรองาน A และ B merge เข้า main ก่อน)
"""
import json
import os

import numpy as np

from angles import compute_angles, ghost_segments
from config import EXERCISES, TEMPLATE_PATH, TOLERANCE
from matrix import apply, build_normalization_matrix, gauss_jordan_inverse, print_explain, reflect_y
from vector import cosine, euclidean, manhattan


def load_templates(exercise):
    """คืน (templates, from_file)
    มี templates.json และมีท่า exercise → ใช้ค่าจากไฟล์, from_file = True
    ไม่มี → ใช้ค่าสมมติใน EXERCISES[exercise]["templates"], from_file = False"""
    raise NotImplementedError("TODO(C)")


def analyze(exercise, image_points, explain=False, templates=None):
    """พิกัดภาพ → result  (key ทั้งหมดดู docs/shared_structure.md)"""
    raise NotImplementedError("TODO(C)")


def print_result(result):
    """พิมพ์มุมที่วัดได้, label ที่ใกล้ที่สุด, ผ่าน/ไม่ผ่านของแต่ละมุม, คำแนะนำ"""
    raise NotImplementedError("TODO(C)")
