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
    groups, clean, seen = {}, {}, set()
    for path in paths:
        with open(path, encoding="utf-8") as f:
            rd = csv.DictReader(f)
            if "exercise" not in (rd.fieldnames or []):
                sys.exit(f"{path} เป็นรูปแบบเก่า (ไม่มีคอลัมน์ exercise) เก็บข้อมูลใหม่ด้วย pose_coach.py")
            for row in rd:
                ex = row["exercise"]
                c = clean.setdefault(ex, {"rows":0, "duplicate":0, "complete":0, "check":0})
                c["rows"] += 1
                key = tuple(row[f"{a}{i}"] for i in range(33) for a in ("x","y"))
                if key in seen:
                    c["duplicate"] += 1
                    continue
                seen.add(key)
                vis = [float(row[f"v{LM[row['side']][k]}"]) for k in NEED[ex]]
                c["complete" if min(vis) >= VIS_MIN else "check"] += 1
                names = [n for n, *_ in EXERCISES[ex]["features"]]
                groups.setdefault(ex,{}).setdefault(row["label"], []).append([float(row[n]) for n in names])
    return {ex: {lab: np.array(r) for lab, r in labs.items()} for ex, labs in groups.items()}, clean


def count_discarded(ex):
    """นับภาพที่ถูกตัดทิ้งตอนเก็บข้อมูล จาก clean_log.csv  คืน {สถานะ: จำนวน}"""
    out = {}
    if os.path.exists(CLEAN_LOG):
        with open(CLEAN_LOG, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["exercise"] == ex and row["status"] != "ok":
                    out[row["status"]] = out.get(row["status"],0) + 1
    return out


def pct(a, b):
    """a เป็นกี่ % ของ b (b = 0 ให้คืน 0.0)"""
    return 100.0 * a / b if b else 0.0


def build_templates(paths):
    """พิมพ์สถิติการ clean และสถิติแต่ละ label แล้วบันทึกค่าเฉลี่ยลง templates.json"""
    raise NotImplementedError("TODO(C)")


def evaluate(paths, test_ratio=0.2, seed=0):
    """แบ่งข้อมูลแต่ละ label เป็น train/test → ท่าต้นแบบ = ค่าเฉลี่ยของ train
    → ทาย test ด้วยท่าต้นแบบที่ Euclidean distance น้อยที่สุด → accuracy + confusion matrix
    (ไม่เขียนทับ templates.json)"""
    raise NotImplementedError("TODO(C)")
