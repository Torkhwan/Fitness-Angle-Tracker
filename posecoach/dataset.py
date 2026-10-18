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
    groups, clean_counts = load_dataset(paths)
    templates = {}
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, encoding="utf-8") as file:
            templates = json.load(file)
    for exercise, label_rows in groups.items():
        counts, discarded = clean_counts[exercise], count_discarded(exercise)
        discarded_count = sum(discarded.values())
        count_before = counts["rows"] + discarded_count
        dropped_count = discarded_count + counts["duplicate"]
        print(f"\n----- {EXERCISES[exercise]['thai_name']} ({exercise}) -----")
        print(f"การ clean: ก่อน {count_before} → หลัง {count_before - dropped_count}")
        print(f"   สมบูรณ์            {counts['complete']:>4}  ({percent(counts['complete'], count_before):5.1f}%)")
        print(f"   ต้องตรวจ/แก้ไข      {counts['check']:>4}  ({percent(counts['check'], count_before):5.1f}%)"
              "  ← บางข้อต่อ visibility ต่ำ ให้เปิดรูปใน results/ ตรวจ label")
        print(f"   ตัดทิ้ง             {dropped_count:>4}  ({percent(dropped_count, count_before):5.1f}%)"
              f"  ← แถวซ้ำ {counts['duplicate']}"
              + "".join(f", {SKIP_REASON[status]} {count}" for status, count in discarded.items()))
        total = sum(len(angle_matrix) for angle_matrix in label_rows.values())
        angle_names = [name for name, *_ in EXERCISES[exercise]["angles"]]
        print(f"ข้อมูลแต่ละแบบ (มุม = {', '.join(angle_names)}):")
        print(f"   {'label':<15}{'n':>4} {'%':>6}   {'mean':<22}{'std':<22}{'min':<22}max")
        templates[exercise] = {}
        for label, angle_matrix in label_rows.items():
            # ท่าต้นแบบของ label = เวกเตอร์ค่าเฉลี่ยของมุมทุกแถว
            templates[exercise][label] = angle_matrix.mean(axis=0).round(2).tolist()
            format_row = lambda values: "[" + ", ".join(f"{value:6.1f}" for value in values) + "]"
            print(f"   {label:<15}{len(angle_matrix):>4} {percent(len(angle_matrix), total):5.1f}%   "
                  f"{format_row(angle_matrix.mean(0)):<22}{format_row(angle_matrix.std(0)):<22}"
                  f"{format_row(angle_matrix.min(0)):<22}{format_row(angle_matrix.max(0))}")
        print(f"   {'รวม':<15}{total:>4}")
    with open(TEMPLATE_PATH, "w", encoding="utf-8") as file:
        json.dump(templates, file, indent=2, ensure_ascii=False)
    print("\nบันทึกท่าต้นแบบ:", TEMPLATE_PATH)

def evaluate(paths, test_ratio=0.2, seed=0):
    """แบ่งข้อมูลแต่ละ label เป็น train/test → ท่าต้นแบบ = ค่าเฉลี่ยของ train
    → ทาย test ด้วยท่าต้นแบบที่ Euclidean distance น้อยที่สุด → accuracy + confusion matrix
    (ไม่เขียนทับ templates.json)
    test_ratio = 0 → ใช้ท่าต้นแบบจริงของโปรแกรม (templates.json) ทายทุกแถว"""
    groups, _ = load_dataset(paths)
    random_generator = np.random.default_rng(seed)
    saved_templates = {}
    if test_ratio == 0:
        if not os.path.exists(TEMPLATE_PATH):
            sys.exit("ไม่พบ templates.json ให้รัน --build-templates ก่อน")
        with open(TEMPLATE_PATH, encoding="utf-8") as file:
            saved_templates = json.load(file)
    for exercise, label_rows in groups.items():
        templates, test_samples = {}, []
        for label, angle_matrix in label_rows.items():
            if test_ratio == 0:
                templates[label] = np.array(saved_templates[exercise][label], float)
                test_samples += [(label, angle_values) for angle_values in angle_matrix]
                continue
            test_count = max(1, round(len(angle_matrix) * test_ratio)) if len(angle_matrix) >= 2 else 0
            shuffled_indices = random_generator.permutation(len(angle_matrix))
            test_samples += [(label, angle_matrix[index]) for index in shuffled_indices[:test_count]]
            templates[label] = angle_matrix[shuffled_indices[test_count:]].mean(axis=0)
        if not test_samples: 
            print(f"[{exercise}] ข้อมูลน้อยเกินไป ต้องมีอย่างน้อย label ละ 2 แถว")
            continue
        labels = list(templates)
        confusion = np.zeros((len(labels), len(labels)), dtype=int)
        for label, angle_values in test_samples:
            predicted_label = min(templates, key=lambda name: euclidean(angle_values, templates[name]))
            confusion[labels.index(label), labels.index(predicted_label)] += 1
        accuracy = percent(np.trace(confusion), confusion.sum())
        print(f"\n----- {EXERCISES[exercise]['thai_name']} ({exercise}) -----")
        row_count = sum(len(angle_matrix) for angle_matrix in label_rows.values())
        train_count = row_count if test_ratio == 0 else row_count - len(test_samples)
        print(f"train {train_count} แถว, test {len(test_samples)} แถว")
        print("Confusion matrix (แถว = label จริง, คอลัมน์ = ที่ระบบทาย):")
        column_width = max(len(label) for label in labels) + 2
        print(" " * column_width + "".join(f"{label:>{column_width}}" for label in labels))
        for index, label in enumerate(labels):
            print(f"{label:<{column_width}}" + "".join(f"{count:>{column_width}}" for count in confusion[index]))
        print(f"Accuracy = {np.trace(confusion)}/{confusion.sum()} = {accuracy:.1f}%")   
