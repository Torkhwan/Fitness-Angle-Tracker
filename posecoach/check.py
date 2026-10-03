"""
check.py  ทดสอบงานของตัวเองทีละส่วน (เขียนเสร็จแล้ว ไม่ต้องแก้)

  python check.py vector      งาน B  ไม่ต้องรอใคร
  python check.py matrix      งาน A  ไม่ต้องรอใคร*
  python check.py normalize   งาน A  ต้องมี vector.norm ของงาน B
  python check.py features    งาน B  ไม่ต้องรอใคร

* matrix.py import norm จาก vector.py แต่ชุด matrix ไม่ได้เรียกใช้ จึงรันได้แม้งาน B ยังไม่เสร็จ
"""
import math
import sys

import numpy as np

A = lambda *v: np.array(v, float)
results = []


def check(name, cond):
    results.append(bool(cond))
    print(f"  {'ผ่าน ✔' if cond else 'ไม่ผ่าน ✘'}  {name}")


def check_vector():
    import vector as v
    check("norm((3,4)) = 5", np.isclose(v.norm(A(3, 4)), 5))
    check("angle_between((1,0),(0,1)) = 90", np.isclose(v.angle_between(A(1, 0), A(0, 1)), 90))
    check("angle_between((1,0),(2,0)) = 0 (ไม่ error จากการปัดเศษ)", np.isclose(v.angle_between(A(1, 0), A(2, 0)), 0))
    check("angle_at((0,0),(1,0),(-1,0)) = 180", np.isclose(v.angle_at(A(0, 0), A(1, 0), A(-1, 0)), 180))
    comp, proj, perp = v.projection(A(3, 4), A(0, 2))
    check("projection((3,4),(0,2)) = 4, (0,4), (3,0)",
          np.isclose(comp, 4) and np.allclose(proj, [0, 4]) and np.allclose(perp, [3, 0]))
    check("cross_z((1,0),(0,1)) = 1, สลับลำดับ = -1",
          np.isclose(v.cross_z(A(1, 0), A(0, 1)), 1) and np.isclose(v.cross_z(A(0, 1), A(1, 0)), -1))
    check("euclidean((3,4,0),(0,0,0)) = 5", np.isclose(v.euclidean(A(3, 4, 0), A(0, 0, 0)), 5))
    check("manhattan((3,-4,1),(0,0,0)) = 8", np.isclose(v.manhattan(A(3, -4, 1), A(0, 0, 0)), 8))
    check("cosine((1,2,3),(2,4,6)) = 1", np.isclose(v.cosine(A(1, 2, 3), A(2, 4, 6)), 1))
    check("signed_from_vertical((1,1)) = 45, ((-1,1)) = -45",
          np.isclose(v.signed_from_vertical(A(1, 1)), 45) and np.isclose(v.signed_from_vertical(A(-1, 1)), -45))


def check_matrix():
    import matrix as m
    check("apply(translation(2,3), (1,1)) = (3,4)", np.allclose(m.apply(m.translation(2, 3), A(1, 1)), [3, 4]))
    check("apply(rotation(0,1), (1,0)) = (0,1)  หมุนทวนเข็ม 90°", np.allclose(m.apply(m.rotation(0, 1), A(1, 0)), [0, 1]))
    check("apply(scaling(2), (1,3)) = (2,6)", np.allclose(m.apply(m.scaling(2), A(1, 3)), [2, 6]))
    check("apply(reflect_x(), (1,3)) = (-1,3)", np.allclose(m.apply(m.reflect_x(), A(1, 3)), [-1, 3]))
    check("apply(reflect_y(), (1,3)) = (1,-3)", np.allclose(m.apply(m.reflect_y(), A(1, 3)), [1, -3]))
    check("ทุกเมทริกซ์เป็น 3×3 ชนิด float",
          all(x.shape == (3, 3) and x.dtype == float for x in
              (m.translation(1, 2), m.rotation(1, 0), m.scaling(2), m.reflect_x(), m.reflect_y())))
    rng = np.random.default_rng(1)
    R = rng.random((3, 3))
    check("det3 ตรงกับ np.linalg.det", np.isclose(m.det3(R), np.linalg.det(R)))
    check("gauss_jordan_inverse ตรงกับ np.linalg.inv", np.allclose(m.gauss_jordan_inverse(R), np.linalg.inv(R)))
    Z = A([0, 1, 2], [1, 0, 3], [4, -3, 8])   # ตำแหน่ง (0,0) เป็น 0 → ต้องสลับแถว
    check("gauss_jordan_inverse เมื่อ pivot แรกเป็น 0 (ต้องสลับแถว)", np.allclose(Z @ m.gauss_jordan_inverse(Z), np.eye(3)))
    try:
        m.gauss_jordan_inverse(A([1, 2, 3], [2, 4, 6], [1, 0, 1]))
        check("เมทริกซ์เอกฐาน → raise ValueError", False)
    except ValueError:
        check("เมทริกซ์เอกฐาน → raise ValueError", True)


def check_normalize():
    import matrix as m
    P = {"S": A(47, 54), "H": A(40, 30), "K": A(56, 42), "A": A(60, 20), "HL": A(59, 13), "TO": A(71, 22)}
    check("floor_vector squat = (12, 9)", np.allclose(m.floor_vector("squat", P), [12, 9]))
    M, info = m.normalization_matrix("squat", P)
    check("M ตรงกับตัวอย่างในข้อเสนอโครงงาน", np.allclose(M, [[0.032, 0.024, -2], [-0.024, 0.032, 0], [0, 0, 1]]))
    check("info: cos 0.8, sin 0.6, theta 36.87, torso 25",
          np.allclose([info["cos"], info["sin"], info["theta"], info["torso"]], [0.8, 0.6, 36.8699, 25], atol=1e-3))
    check("info มี key ครบ", set(info) == {"T", "F", "R", "S", "floor", "cos", "sin", "theta", "torso"})
    check("สะโพก → (0,0), ไหล่ → (0.8,0.6)", np.allclose(m.apply(M, P["H"]), [0, 0]) and np.allclose(m.apply(M, P["S"]), [0.8, 0.6]))
    check("det3(M) = 1/25² = 0.0016", np.isclose(m.det3(M), 0.0016))
    check("M⁻¹ = [[20,-15,40],[15,20,30],[0,0,1]]", np.allclose(m.gauss_jordan_inverse(M), [[20, -15, 40], [15, 20, 30], [0, 0, 1]]))
    Pm = {k: A(-p[0], p[1]) for k, p in P.items()}   # คนเดิมแต่หันซ้าย
    M2, info2 = m.normalization_matrix("squat", Pm)
    check("หันซ้าย → ใช้ Fx และได้จุดหลัง normalize เท่าเดิม",
          info2["F"][0, 0] == -1 and all(np.allclose(m.apply(M2, Pm[k]), m.apply(M, P[k])) for k in P))


def check_features():
    import features as f
    Q = {"S": A(0.8, 0.6), "H": A(0, 0), "K": A(0.8, 0), "A": A(0.4, -0.8), "HL": A(0.2, -1.0), "TO": A(0.8, -1.0)}
    x, extra = f.compute_features("squat", Q)
    check("squat = [63.43, 36.87, 53.13]", np.allclose(x, [63.4349, 36.8699, 53.1301], atol=1e-3))
    Q = {"S": A(1, 0), "E": A(0.7, -0.3), "W": A(1, -0.6), "H": A(0, 0), "K": A(-0.8, 0), "A": A(-1.5, 0), "TO": A(-1.6, -0.6)}
    x, _ = f.compute_features("pushup", Q)
    check("pushup ลำตัวตรง = [90, 0, 0]", np.allclose(x, [90, 0, 0], atol=1e-6))
    x, _ = f.compute_features("pushup", {**Q, "H": A(0, -0.25)})
    check("pushup สะโพกตก → hip_dev ติดลบ", x[1] < -10)
    x, _ = f.compute_features("pushup", {**Q, "H": A(0, 0.25)})
    check("pushup สะโพกโด่ง → hip_dev เป็นบวก", x[1] > 10)
    raw = {"S": A(0, 1), "H": A(0, 0), "K_L": A(0.9, 0), "A_L": A(0.9, -0.9), "HL_L": A(0.8, -1.0), "TO_L": A(1.1, -1.0),
           "K_R": A(-0.45, -0.8), "A_R": A(-1.2, -0.75), "HL_R": A(-1.3, -0.8), "TO_R": A(-1.05, -1.0)}
    Ql = f.prepare_points("lunge", raw)
    check("prepare_points lunge: key = S H Kf Af HLf TOf Kb Ab HLb TOb, ขาหน้า = ซ้าย",
          set(Ql) == {"S", "H", "Kf", "Af", "HLf", "TOf", "Kb", "Ab", "HLb", "TOb"} and np.allclose(Ql["Kf"], raw["K_L"]))
    mirror = {k: A(-p[0], p[1]) for k, p in raw.items()}
    check("prepare_points lunge: หันซ้ายก็ยังเลือกขาหน้าถูก", np.allclose(f.prepare_points("lunge", mirror)["Kf"], mirror["K_L"]))
    check("prepare_points ท่าอื่นคืนค่าเดิม", f.prepare_points("squat", Q) is Q)
    x, _ = f.compute_features("lunge", Ql)
    check("lunge = [90, 0, 0]", np.allclose(x, [90, 0, 0], atol=1e-6))
    seg = f.ghost_segments("squat", {"H": A(0, 0)}, A(65, 55, 30))
    check("ghost squat: เส้นจากสะโพกไป (sin30°, cos30°)", len(seg) == 1 and np.allclose(seg[0][1], [0.5, math.sqrt(3) / 2]))
    seg = f.ghost_segments("pushup", {**Q, "H": A(0, -0.25)}, A(90, 0, 5))
    check("ghost pushup: สะโพกที่ถูกอยู่บนเส้นไหล่-ข้อเท้า", len(seg) == 2 and np.allclose(seg[0][1], [0, 0]))


if __name__ == "__main__":
    sets = {"vector": check_vector, "matrix": check_matrix, "normalize": check_normalize, "features": check_features}
    if len(sys.argv) != 2 or sys.argv[1] not in sets:
        sys.exit("ใช้: python check.py " + " | ".join(sets))
    try:
        sets[sys.argv[1]]()
    except NotImplementedError as e:
        sys.exit(f"ยังมีฟังก์ชันที่ไม่ได้เขียน: {e}")
    print(f"\n{sys.argv[1]}: ผ่าน {sum(results)}/{len(results)}")
    sys.exit(0 if all(results) else 1)
