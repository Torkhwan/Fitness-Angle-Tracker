"""
selftest.py  ทดสอบรวมทั้งระบบ (เขียนเสร็จแล้ว ไม่ต้องแก้)

  python selftest.py

ต้องผ่านทุกข้อก่อนเริ่มเก็บข้อมูล ใช้ได้เมื่องาน A, B, C merge เข้า main ครบแล้ว
"""
import math
import sys

import numpy as np

from analyze import analyze, print_result
from config import EXERCISES
from angles import prepare_points
from matrix import apply, det3, gauss_jordan_inverse, reflect_x, reflect_y, rotation, scaling, translation


def random_view(pts_math, rng):
    """จำลองการถ่ายภาพ: หมุนกล้อง ±25°, ย่อขยาย, เลื่อน, (อาจ) หันซ้าย แล้วเป็นพิกัดภาพ y ชี้ลง"""
    a = math.radians(rng.uniform(-25, 25))
    k = rng.uniform(50, 300)
    mirror = rng.random() < 0.5
    G = translation(rng.uniform(300, 600), rng.uniform(300, 600)) @ reflect_y() @ scaling(k) \
        @ rotation(math.cos(a), math.sin(a)) @ (reflect_x() if mirror else np.eye(3))
    return {n: apply(G, np.array(v, float)) for n, v in pts_math.items()}


def selftest():
    ok_all = True
    fixed = lambda ex: {k: np.array(v, float) for k, v in EXERCISES[ex]["templates"].items()}

    # (ก) ตัวอย่างในข้อเสนอโครงงาน — ตัวเลขต้องตรง
    doc = {"S": (47, 54), "H": (40, 30), "K": (56, 42), "A": (60, 20), "HL": (59, 13), "TO": (71, 22)}
    r = analyze("squat", {k: np.array([v[0], -v[1]], float) for k, v in doc.items()},
                explain=True, templates=fixed("squat"))
    ok = (np.allclose(r["x"], [63.4349, 36.8699, 53.1301], atol=1e-3)
          and np.allclose(r["M"], [[0.032, 0.024, -2], [-0.024, 0.032, 0], [0, 0, 1]])
          and np.allclose(r["M_inv"], [[20, -15, 40], [15, 20, 30], [0, 0, 1]])
          and r["ranking"][0]["name"] == "lean_forward" and abs(r["ranking"][0]["euclid"] - 3.07) < 0.01)
    print_result(r)
    print("  (ก) ตัวอย่างในข้อเสนอโครงงาน:", "ผ่าน ✔" if ok else "ไม่ผ่าน ✘")
    ok_all &= ok

    # (ข) ท่าที่สร้างขึ้นซึ่งรู้คำตอบ + ถ่ายจากมุมสุ่ม 50 ครั้ง ต้องได้ features เท่าเดิม
    cases = {
        "pushup": ({"S": (1, 0), "E": (0.7, -0.3), "W": (1, -0.6), "H": (0, 0), "K": (-0.8, 0),
                    "A": (-1.5, 0), "TO": (-1.6, -0.6)}, [90, 0, 0], "correct"),
        "lunge": ({"S": (0, 1), "H": (0, 0), "K_L": (0.9, 0), "A_L": (0.9, -0.9), "HL_L": (0.8, -1.0),
                   "TO_L": (1.1, -1.0), "K_R": (-0.45, -0.8), "A_R": (-1.2, -0.75),
                   "HL_R": (-1.3, -0.8), "TO_R": (-1.05, -1.0)}, [90, 0, 0], "correct"),
    }
    sag = dict(cases["pushup"][0]); sag["H"] = (0, -0.25)
    rng = np.random.default_rng(7)
    for ex, (pose, expect, best) in cases.items():
        ok = True
        for _ in range(50):
            pts = prepare_points(ex, random_view(pose, rng))
            rr = analyze(ex, pts, templates=fixed(ex))
            ok &= np.allclose(rr["x"], expect, atol=1e-6) and rr["ranking"][0]["name"] == best
            ok &= np.allclose(rr["M"] @ rr["M_inv"], np.eye(3))
        print(f"  (ข) {EXERCISES[ex]['th']}: มุม {np.round(rr['x'], 2)} คงที่ทุกมุมกล้อง →", "ผ่าน ✔" if ok else "ไม่ผ่าน ✘")
        ok_all &= ok
    rr = analyze("pushup", random_view(sag, rng), templates=fixed("pushup"))
    ok = rr["x"][1] < -10 and rr["ranking"][0]["name"] == "hip_sag"
    print(f"  (ค) วิดพื้นสะโพกตก: hip_dev = {rr['x'][1]:.2f}° → {rr['ranking'][0]['name']} →", "ผ่าน ✔" if ok else "ไม่ผ่าน ✘")
    ok_all &= ok
    M = rng.random((3, 3))
    ok = np.allclose(gauss_jordan_inverse(M), np.linalg.inv(M)) and np.isclose(det3(M), np.linalg.det(M))
    print("  (ง) Gauss-Jordan / det3 เทียบกับ NumPy:", "ผ่าน ✔" if ok else "ไม่ผ่าน ✘")
    ok_all &= ok
    print("\nSELFTEST:", "ผ่านทั้งหมด ✔" if ok_all else "มีข้อไม่ผ่าน ✘")
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)
