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

from config import CLEAN_LOG, EXERCISES, LANDMARK_INDEX, REQUIRED_POINTS, SKIP_REASON, TEMPLATE_PATH, VISIBILITY_MIN
from vector import euclidean


def load_dataset(paths):
    """อ่าน CSV → ตัดแถวซ้ำ → คืน ({ท่า: {label: เมทริกซ์ n×3}}, {ท่า: ตัวนับการ clean})
    แถวซ้ำ = พิกัด 66 ค่าเหมือนกันทุกตัว (เช่น กดบันทึกเฟรมเดียวกัน 2 ครั้ง)
    สมบูรณ์ = ข้อต่อที่ท่านั้นใช้มี visibility ≥ VISIBILITY_MIN ทุกจุด, ต้องตรวจ = มีบางจุดต่ำกว่า"""
    groups, clean_counts, seen_rows = {}, {}, set()
    for path in paths:
        with open(path, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if "exercise" not in (reader.fieldnames or []):
                sys.exit(f"{path} เป็นรูปแบบเก่า (ไม่มีคอลัมน์ exercise) เก็บข้อมูลใหม่ด้วย pose_coach.py")
            for row in reader:
                exercise = row["exercise"]
                counts = clean_counts.setdefault(exercise, {"rows":0, "duplicate":0, "complete":0, "check":0})
                counts["rows"] += 1
                row_key = tuple(row[f"{axis}{index}"] for index in range(33) for axis in ("x","y"))
                if row_key in seen_rows:
                    counts["duplicate"] += 1
                    continue
                seen_rows.add(row_key)
                visibility = [float(row[f"v{LANDMARK_INDEX[row['side']][point_name]}"])
                              for point_name in REQUIRED_POINTS[exercise]]
                counts["complete" if min(visibility) >= VISIBILITY_MIN else "check"] += 1
                angle_names = [name for name, *_ in EXERCISES[exercise]["angles"]]
                groups.setdefault(exercise,{}).setdefault(row["label"], []).append(
                    [float(row[name]) for name in angle_names])
    return {exercise: {label: np.array(rows) for label, rows in label_rows.items()}
            for exercise, label_rows in groups.items()}, clean_counts


def count_discarded(exercise):
    """นับภาพที่ถูกตัดทิ้งตอนเก็บข้อมูล จาก clean_log.csv  คืน {สถานะ: จำนวน}"""
    status_counts = {}
    if os.path.exists(CLEAN_LOG):
        with open(CLEAN_LOG, encoding="utf-8") as file:
            for row in csv.DictReader(file):
                if row["exercise"] == exercise and row["status"] != "ok":
                    status_counts[row["status"]] = status_counts.get(row["status"],0) + 1
    return status_counts


def percent(part, whole):
    """part เป็นกี่ % ของ whole (whole = 0 ให้คืน 0.0)"""
    return 100.0 * part / whole if whole else 0.0


def build_templates(paths):
    """พิมพ์สถิติการ clean และสถิติแต่ละ label แล้วบันทึกค่าเฉลี่ยลง templates.json"""
    raise NotImplementedError("TODO(C)")


def evaluate(paths, test_ratio=0.2, seed=0):
    """แบ่งข้อมูลแต่ละ label เป็น train/test → ท่าต้นแบบ = ค่าเฉลี่ยของ train
    → ทาย test ด้วยท่าต้นแบบที่ Euclidean distance น้อยที่สุด → accuracy + confusion matrix
    (ไม่เขียนทับ templates.json)"""
    raise NotImplementedError("TODO(C)")
