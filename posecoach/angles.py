"""
angles.py  งาน B: เตรียมจุด → มุมของแต่ละท่า → เส้นท่าที่ถูก

คำอธิบายงานและสูตร: docs/vector_angles.md
ทดสอบ: python check.py angles
"""
import math

import numpy as np

from vector import angle_at, angle_between, cross_z, norm, projection, signed_from_vertical, vertical_unit_vector


def prepare_points(exercise, points):
    """ท่า lunge: แยกขาหน้า/ขาหลัง (ขาหน้า = ข้อเท้าที่อยู่ไปทางทิศที่ปลายเท้าชี้)
        ท่าอื่นคืน points เดิม"""
    if exercise != 'lunge':
        return points

    facing = ((points['left_toe_point'] - points['left_heel_point'])
              + (points['right_toe_point'] - points['right_heel_point']))

    direction_sign = 1.0 if facing[0] >= 0 else -1.0

    if direction_sign * points['left_ankle_point'][0] >= direction_sign * points['right_ankle_point'][0]:
        front_side, back_side = 'left', 'right'
    else:
        front_side, back_side = 'right', 'left'

    return {
        'shoulder_point': points['shoulder_point'],
        'hip_point': points['hip_point'],
        'front_knee_point': points[f'{front_side}_knee_point'],
        'front_ankle_point': points[f'{front_side}_ankle_point'],
        'front_heel_point': points[f'{front_side}_heel_point'],
        'front_toe_point': points[f'{front_side}_toe_point'],
        'back_knee_point': points[f'{back_side}_knee_point'],
        'back_ankle_point': points[f'{back_side}_ankle_point'],
        'back_heel_point': points[f'{back_side}_heel_point'],
        'back_toe_point': points[f'{back_side}_toe_point']
    }


def compute_angles(exercise, normalized_points):
    """normalized_points = จุดหลัง normalize (หันไปทาง +x, y ชี้ขึ้น, สะโพกที่ 0, ลำตัวยาว 1)
        คืน (angle_values, extra)  angle_values = np.array 3 ค่า เรียงตาม EXERCISES[exercise]["angles"],
        extra = dict ค่าประกอบ"""
    if exercise == 'squat':
        knee_point, hip_point = normalized_points['knee_point'], normalized_points['hip_point']
        ankle_point, shoulder_point = normalized_points['ankle_point'], normalized_points['shoulder_point']
        toe_point = (normalized_points['toe_point'] if 'toe_point' in normalized_points
                     else normalized_points.get('left_toe_point', np.array([0.0, 0.0])))

        knee = angle_at(knee_point, hip_point, ankle_point)
        hip = angle_at(hip_point, shoulder_point, knee_point)

        torso_vector = shoulder_point - hip_point
        component, projected, perpendicular = projection(torso_vector, vertical_unit_vector)
        lean = math.degrees(math.acos(max(-1.0, min(1.0, component / norm(torso_vector)))))

        angle_values = np.array([knee, hip, lean])
        extra = {
            "torso_vector": torso_vector,
            "component บน ĵ": component,
            "projection บน ĵ": projected,
            "ส่วนตั้งฉาก": perpendicular,
            "เข่าเลยปลายเท้า (เท่าลำตัว)": float(knee_point[0] - toe_point[0])
        }

    elif exercise == 'pushup':
        elbow_point, shoulder_point = normalized_points['elbow_point'], normalized_points['shoulder_point']
        wrist_point, hip_point = normalized_points['wrist_point'], normalized_points['hip_point']
        ankle_point = normalized_points['ankle_point']

        elbow = angle_at(elbow_point, shoulder_point, wrist_point)
        body_angle = angle_at(hip_point, shoulder_point, ankle_point)
        body_line = shoulder_point - ankle_point
        cross_value = cross_z(body_line, hip_point - ankle_point)
        hip_deviation = (180.0 - body_angle) * (1.0 if cross_value >= 0 else -1.0)
        tilt = angle_between(body_line, np.array([1.0, 0.0]))

        _, _, perpendicular = projection(hip_point - ankle_point, body_line)

        angle_values = np.array([elbow, hip_deviation, tilt])
        extra = {
            "มุมลำตัวที่สะโพก": body_angle,
            "cross product (z)": cross_value,
            "ระยะสะโพกจากเส้น ไหล่-ข้อเท้า": perpendicular
        }

    elif exercise == 'lunge':
        front_knee_point, hip_point = normalized_points['front_knee_point'], normalized_points['hip_point']
        front_ankle_point = normalized_points['front_ankle_point']
        back_knee_point, back_ankle_point = normalized_points['back_knee_point'], normalized_points['back_ankle_point']
        shoulder_point, front_toe_point = normalized_points['shoulder_point'], normalized_points['front_toe_point']

        front_knee = angle_at(front_knee_point, hip_point, front_ankle_point)
        shin = signed_from_vertical(front_knee_point - front_ankle_point)
        lean = abs(signed_from_vertical(shoulder_point - hip_point))

        angle_values = np.array([front_knee, shin, lean])
        extra = {
            "มุมเข่าหลัง": angle_at(back_knee_point, hip_point, back_ankle_point),
            "เข่าหน้าเลยปลายเท้า (เท่าลำตัว)": float(front_knee_point[0] - front_toe_point[0])
        }

    return angle_values, extra


def ghost_segments(exercise, normalized_points, correct_template):
    """ท่าที่ถูก (พิกัดมาตรฐาน) สำหรับวาดทับ จะถูกแปลงกลับด้วย inverse_matrix ใน analyze
        correct_template = มุม 3 ค่าของท่าต้นแบบ correct, คืน list ของ (จุดเริ่ม, จุดปลาย)"""
    segments = []

    if exercise == 'squat':
        hip_point = normalized_points['hip_point']
        lean_angle = math.radians(correct_template[2])
        torso_direction = np.array([math.sin(lean_angle), math.cos(lean_angle)])
        segments.append((hip_point, hip_point + torso_direction))

    elif exercise == 'pushup':
        shoulder_point, ankle_point = normalized_points['shoulder_point'], normalized_points['ankle_point']
        hip_point = normalized_points['hip_point']
        body_line = shoulder_point - ankle_point
        _, projected, _ = projection(hip_point - ankle_point, body_line)
        correct_hip_point = ankle_point + projected

        segments.append((shoulder_point, correct_hip_point))
        segments.append((correct_hip_point, ankle_point))

    elif exercise == 'lunge':
        front_ankle_point, front_knee_point = normalized_points['front_ankle_point'], normalized_points['front_knee_point']
        hip_point = normalized_points['hip_point']

        shin_angle = math.radians(correct_template[1])
        correct_shin_vector = (norm(front_knee_point - front_ankle_point)
                               * np.array([math.sin(shin_angle), math.cos(shin_angle)]))
        segments.append((front_ankle_point, front_ankle_point + correct_shin_vector))

        lean_angle = math.radians(correct_template[2])
        lean_direction = np.array([math.sin(lean_angle), math.cos(lean_angle)])
        segments.append((hip_point, hip_point + lean_direction))

    return segments
