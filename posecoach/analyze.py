"""
analyze.py  งาน C: เทียบท่าต้นแบบและสรุปผล

คำอธิบายงานและสูตร: docs/role_C_analyze.md
ทดสอบ: python selftest.py  (ต้องรองาน A และ B merge เข้า main ก่อน)
"""
import json
import os

import numpy as np

from config import EXERCISES, TEMPLATE_PATH, TOLERANCE
from angles import compute_features, ghost_segments
from matrix import apply, gauss_jordan_inverse, normalization_matrix, print_explain, reflect_y
from vector import cosine, euclidean, manhattan


def load_templates(ex):
    """คืน (templates, from_file)
    มี templates.json และมีท่า ex → ใช้ค่าจากไฟล์, from_file = True
    ไม่มี → ใช้ค่าสมมติใน EXERCISES[ex]["templates"], from_file = False"""
    raise NotImplementedError("TODO(C)")


def analyze(ex, pts_img, explain=False, templates=None):
    """พิกัดภาพ → result dict r  (key ทั้งหมดดู docs/shared_structure.md)"""
    raise NotImplementedError("TODO(C)")


def print_result(r):
    """พิมพ์ features, label ที่ใกล้ที่สุด, ผ่าน/ไม่ผ่านของแต่ละมุม, คำแนะนำ"""
    raise NotImplementedError("TODO(C)")
