"""
analyze.py  งาน C: เทียบท่าต้นแบบและสรุปผล

คำอธิบายงานและสูตร: docs/analyze_dataset.md
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
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, encoding="utf-8") as file:
            saved_templates = json.load(file)
        if exercise in saved_templates:
            return {label: np.array(values, float) for label, values in saved_templates[exercise].items()}, True
    return {label: np.array(values, float) for label, values in EXERCISES[exercise]["templates"].items()}, False


def analyze(exercise, image_points, explain=False, templates=None):
    """พิกัดภาพ → result  (key ทั้งหมดดู docs/data_structure.md)"""
    exercise_config = EXERCISES[exercise]
    flip_y_matrix = reflect_y()
    flipped_points = {point_name: apply(flip_y_matrix, point) for point_name, point in image_points.items()}
    normalization_matrix, info = build_normalization_matrix(exercise, flipped_points)
    normalized_points = {point_name: apply(normalization_matrix, point)
                         for point_name, point in flipped_points.items()}
    angle_values, extra = compute_angles(exercise, normalized_points)
    from_file = False
    if templates is None:
        templates, from_file = load_templates(exercise)
    ranking = sorted(({"name": label, "euclidean": euclidean(angle_values, template),
                       "manhattan": manhattan(angle_values, template), "cosine": cosine(angle_values, template)}
                      for label, template in templates.items()), key=lambda entry: entry["euclidean"])
    correct_template = templates.get("correct", next(iter(templates.values())))
    difference = angle_values - correct_template
    checks, tips = [], []
    for index, (_, thai_name, message_when_higher, message_when_lower) in enumerate(exercise_config["angles"]):
        checks.append((thai_name, difference[index], abs(difference[index]) <= TOLERANCE))
        if difference[index] > TOLERANCE and message_when_higher:
            tips.append(message_when_higher.format(difference=difference[index]))
        elif difference[index] < -TOLERANCE and message_when_lower:
            tips.append(message_when_lower.format(difference=-difference[index]))
    inverse_matrix = gauss_jordan_inverse(normalization_matrix)
    # เส้นท่าที่ถูกอยู่ในพิกัดมาตรฐาน → แปลงกลับเป็นพิกัดภาพ
    ghosts = [tuple(apply(flip_y_matrix, apply(inverse_matrix, point)) for point in segment)
              for segment in ghost_segments(exercise, normalized_points, correct_template)]
    result = {"exercise": exercise, "angle_values": angle_values, "ranking": ranking, "checks": checks,
              "tips": tips, "normalization_matrix": normalization_matrix, "inverse_matrix": inverse_matrix,
              "info": info, "normalized_points": normalized_points, "flipped_points": flipped_points,
              "extra": extra, "ghosts": ghosts, "from_file": from_file}
    if explain:
        print_explain(image_points, result)
    return result

def print_result(result):
    """พิมพ์มุมที่วัดได้, label ที่ใกล้ที่สุด, ผ่าน/ไม่ผ่านของแต่ละมุม, คำแนะนำ"""
    exercise_config = EXERCISES[result["exercise"]]
    best_label = result["ranking"][0]["name"]
    print(f"[{exercise_config['thai_name']}] มุม = " + ", ".join(f"{value:.1f}" for value in result["angle_values"]))
    print(f"ผล: ใกล้เคียง \"{exercise_config['labels'].get(best_label, best_label)}\" มากที่สุด")
    for thai_name, difference, passed in result["checks"]:
        print(f"   {thai_name:<24} ต่างจากท่าถูก {difference:+6.1f}°  {'ผ่าน' if passed else 'ไม่ผ่าน'}")
    for tip in result["tips"]:
        print("   คำแนะนำ:", tip)
    if not result["from_file"]:
        print("   (ยังใช้ท่าต้นแบบค่าสมมติ — เก็บข้อมูลแล้วรัน --build-templates)")
