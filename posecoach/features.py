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
    if ex != 'lunge':
        return pts

    facing = (pts['TO_L'] - pts['HL_L']) + (pts['TO_R'] - pts['HL_R'])

    s = 1.0 if facing[0] >= 0 else -1.0

    if s * pts['A_L'][0] >= s * pts['A_R'][0]:
        front, back = 'L', 'R'
    else:
        front, back = 'R', 'L'

    return {
        'S': pts['S'],
        'H': pts['H'],
        'Kf': pts[f'K_{front}'],
        'Af': pts[f'A_{front}'],
        'HLf': pts[f'HL_{front}'],
        'TOf': pts[f'TO_{front}'],
        'Kb': pts[f'K_{back}'],
        'Ab': pts[f'A_{back}'],
        'HLb': pts[f'HL_{back}'],
        'TOb': pts[f'TO_{back}']
    }


def compute_features(ex, Q):
    """Q = จุดหลัง normalize (หันไปทาง +x, y ชี้ขึ้น, สะโพกที่ 0, ลำตัวยาว 1)
        คืน (x, extra)  x = np.array 3 ค่า เรียงตาม EXERCISES[ex]["features"], extra = dict ค่าประกอบ"""
    if ex == 'squat':
        K, H, A, S = Q['K'], Q['H'], Q['A'], Q['S']
        TO = Q['TO'] if 'TO' in Q else Q.get('TO_L', np.array([0.0, 0.0]))

        knee = angle_at(K, H, A)
        hip = angle_at(H, S, K)

        t = S - H
        comp, proj, perp = projection(t, J)
        lean = math.degrees(math.acos(max(-1.0, min(1.0, comp / norm(t)))))

        features = np.array([knee, hip, lean])
        extra = {
            "torso t": t,
            "comp_ĵ t": comp,
            "proj_ĵ t": proj,
            "ส่วนตั้งฉาก": perp,
            "เข่าเลยปลายเท้า (เท่าลำตัว)": float(K[0] - TO[0])
        }

    elif ex == 'pushup':
        E, S, W, H, A = Q['E'], Q['S'], Q['W'], Q['H'], Q['A']

        elbow = angle_at(E, S, W)
        body = angle_at(H, S, A)
        line = S - A
        cz = cross_z(line, H - A)
        hip_dev = (180.0 - body) * (1.0 if cz >= 0 else -1.0)
        tilt = angle_between(line, np.array([1.0, 0.0]))

        _, _, perp = projection(H - A, line)

        features = np.array([elbow, hip_dev, tilt])
        extra = {
            "มุมลำตัวที่สะโพก": body,
            "cross z": cz,
            "ระยะสะโพกจากเส้น ไหล่-ข้อเท้า": perp
        }

    elif ex == 'lunge':
        Kf, H, Af = Q['Kf'], Q['H'], Q['Af']
        Kb, Ab = Q['Kb'], Q['Ab']
        S, TOf = Q['S'], Q['TOf']

        front_knee = angle_at(Kf, H, Af)
        shin = signed_from_vertical(Kf - Af)
        lean = abs(signed_from_vertical(S - H))

        features = np.array([front_knee, shin, lean])
        extra = {
            "มุมเข่าหลัง": angle_at(Kb, H, Ab),
            "เข่าหน้าเลยปลายเท้า (เท่าลำตัว)": float(Kf[0] - TOf[0])
        }

    return features, extra


def ghost_segments(ex, Q, ref):
    """ท่าที่ถูก (พิกัดมาตรฐาน) สำหรับวาดทับ จะถูกแปลงกลับด้วย M⁻¹ ใน analyze
        ref = features ของท่าต้นแบบ correct, คืน list ของ (จุดเริ่ม, จุดปลาย)"""
    segments = []

    if ex == 'squat':
        H = Q['H']
        a = math.radians(ref[2])
        dir_torso = np.array([math.sin(a), math.cos(a)])
        segments.append((H, H + dir_torso))

    elif ex == 'pushup':
        S, A, H = Q['S'], Q['A'], Q['H']
        line = S - A
        _, proj, _ = projection(H - A, line)
        hg = A + proj
        
        segments.append((S, hg))
        segments.append((hg, A))

    elif ex == 'lunge':
        Af, H = Q['Af'], Q['H']

        a_shin = math.radians(ref[1])
        dir_shin = np.array([math.sin(a_shin), math.cos(a_shin)])
        segments.append((Af, Af + dir_shin))

        a_lean = math.radians(ref[2])
        dir_lean = np.array([math.sin(a_lean), math.cos(a_lean)])
        segments.append((H, H + dir_lean))

    return segments