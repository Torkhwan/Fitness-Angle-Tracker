"""
dataset.py  งาน C: อ่านข้อมูล, clean, สถิติ, สร้างท่าต้นแบบ, วัดความแม่นยำ

คำอธิบายงานและสูตร: docs/role_C_analyze.md
ทดสอบ: python pose_coach.py --build-templates data_squat.csv   (หลังเก็บข้อมูลแล้ว)
"""
import csv
import json
import os
import sys

import numpy as np

from config import CLEAN_LOG, EXERCISES, LM, NEED, SKIP_REASON, TEMPLATE_PATH, VIS_MIN
from vector import euclidean


def load_dataset(paths):
    """อ่าน CSV → ตัดแถวซ้ำ → คืน ({ท่า: {label: เมทริกซ์ n×3}}, {ท่า: ตัวนับการ clean})
    แถวซ้ำ = พิกัด 66 ค่าเหมือนกันทุกตัว (เช่น กดบันทึกเฟรมเดียวกัน 2 ครั้ง)
    สมบูรณ์ = ข้อต่อที่ท่านั้นใช้มี visibility ≥ VIS_MIN ทุกจุด, ต้องตรวจ = มีบางจุดต่ำกว่า"""
    raise NotImplementedError("TODO(C)")


def count_discarded(ex):
    """นับภาพที่ถูกตัดทิ้งตอนเก็บข้อมูล จาก clean_log.csv  คืน {สถานะ: จำนวน}"""
    raise NotImplementedError("TODO(C)")


def pct(a, b):
    """a เป็นกี่ % ของ b (b = 0 ให้คืน 0.0)"""
    raise NotImplementedError("TODO(C)")


def build_templates(paths):
    """พิมพ์สถิติการ clean และสถิติแต่ละ label แล้วบันทึกค่าเฉลี่ยลง templates.json"""
    raise NotImplementedError("TODO(C)")


def evaluate(paths, test_ratio=0.2, seed=0):
    """แบ่งข้อมูลแต่ละ label เป็น train/test → ท่าต้นแบบ = ค่าเฉลี่ยของ train
    → ทาย test ด้วยท่าต้นแบบที่ Euclidean distance น้อยที่สุด → accuracy + confusion matrix
    (ไม่เขียนทับ templates.json)"""
    raise NotImplementedError("TODO(C)")
