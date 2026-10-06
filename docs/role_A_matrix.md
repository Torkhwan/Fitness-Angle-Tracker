# งาน A: เมทริกซ์

ไฟล์: `posecoach/matrix.py` | ส่งภายใน **7 ต.ค. 69** | ทฤษฎี: บท 4, 5, 7, 8, 9

อ่าน [shared_structure.md](shared_structure.md) ข้อ 2, 3, 7, 8 ก่อน

## งานนี้ทำอะไร

ภาพแต่ละภาพถ่ายใกล้-ไกล เอียง และหันซ้าย-ขวาไม่เหมือนกัน งาน A สร้างเมทริกซ์ `normalization_matrix` (M) ที่ย้ายทุกภาพมาอยู่ในพิกัดมาตรฐานเดียวกัน เพื่อให้มุมที่งาน B วัดได้เทียบกันได้ และสร้าง `inverse_matrix` (M⁻¹) เพื่อแปลงเส้นท่าที่ถูกกลับไปวาดบนภาพ

ห้ามใช้ `np.linalg.det` และ `np.linalg.inv` (ใช้ `@` คูณเมทริกซ์ได้)

## ส่วนที่ 1: เมทริกซ์การแปลง (ทำก่อน ไม่ต้องรอใคร)

ทุกฟังก์ชันคืน `np.array` 3×3 โดยใส่ `dtype=float`

| ฟังก์ชัน | เมทริกซ์ |
|---|---|
| `translation(shift_x, shift_y)` | `[[1, 0, shift_x], [0, 1, shift_y], [0, 0, 1]]` |
| `rotation(cos_theta, sin_theta)` | `[[cos, −sin, 0], [sin, cos, 0], [0, 0, 1]]` |
| `scaling(scale_factor)` | `[[scale_factor, 0, 0], [0, scale_factor, 0], [0, 0, 1]]` |
| `reflect_x()` | `[[−1, 0, 0], [0, 1, 0], [0, 0, 1]]` |
| `reflect_y()` | `[[1, 0, 0], [0, −1, 0], [0, 0, 1]]` |

`rotation` รับ cos กับ sin โดยตรง (ไม่รับมุม) เพราะตอน normalize เราได้ cos θ, sin θ จากเวกเตอร์แนวพื้นอยู่แล้ว ไม่ต้องหา θ ก่อน และ R(−θ) ได้จากการส่ง `−sin_theta` เข้าไป

เหตุที่เป็น 3×3: การเลื่อน (translation) เขียนเป็นการคูณเมทริกซ์ 2×2 ไม่ได้ จึงเพิ่มพิกัดตัวที่สามเป็น 1 (homogeneous coordinates) ทำให้เลื่อน หมุน ย่อขยาย สะท้อน คูณรวมเป็นเมทริกซ์เดียวได้

**`apply(matrix, point)`** รับจุด 2 มิติ `point`

1. สร้างเวกเตอร์ `[point[0], point[1], 1.0]`
2. คูณ `matrix @` เวกเตอร์นั้น
3. คืนเฉพาะ 2 ค่าแรก

**`determinant_3x3(matrix)`** cofactor expansion ตามแถวแรก

```
det = a(ei − fh) − b(di − fg) + c(dh − eg)      เมื่อ matrix = [[a, b, c], [d, e, f], [g, h, i]]
```

`a` ถึง `i` เป็นชื่อสมาชิกของเมทริกซ์ตามสูตร ใช้ตัวอักษรเดี่ยวได้เฉพาะในฟังก์ชันนี้

**`gauss_jordan_inverse(matrix)`** ทำ `[M | I] → [I | M⁻¹]`

1. `size` = จำนวนแถว, สร้างเมทริกซ์แต่งเติม `augmented` = `matrix` (แปลงเป็น float) ต่อด้วยเมทริกซ์เอกลักษณ์ขนาด `size` ทางขวา (`np.hstack`, `np.eye`)
2. วนทีละคอลัมน์ `column` = 0 ถึง `size − 1`
   1. หาแถว `pivot_row` ตั้งแต่แถว `column` ลงไป ที่ค่าสัมบูรณ์ในคอลัมน์ `column` มากที่สุด (partial pivoting)
   2. ถ้าค่านั้นเล็กกว่า `1e-12` → `raise ValueError("Singular matrix (det = 0)")`
   3. สลับแถว `column` กับแถว `pivot_row`
   4. หารแถว `column` ทั้งแถวด้วยตัว pivot ให้ตัวนำเป็น 1
   5. ทุกแถว `row` ที่ไม่ใช่ `column`: แถว `row` ← แถว `row` − (ค่าของแถว `row` ในคอลัมน์ `column`) × แถว `column`
3. คืนครึ่งขวาของ `augmented` (คอลัมน์ `size` เป็นต้นไป)

ชนิดของ error ต้องเป็น `ValueError` เท่านั้น เพราะงาน D ดักชนิดนี้เพื่อบันทึกสถานะ `calc_error`

ทดสอบ

```bash
python check.py matrix
```

## ส่วนที่ 2: Normalize (ต้องมี `norm` ของงาน B)

**`floor_vector(exercise, flipped_points)`** เวกเตอร์แนวพื้นที่ชี้ไปทางด้านหน้าของคน

| ท่า | เวกเตอร์แนวพื้น |
|---|---|
| `squat` | `flipped_points["toe_point"] − flipped_points["heel_point"]` ส้นเท้า → ปลายเท้า |
| `pushup` | `flipped_points["wrist_point"] − flipped_points["toe_point"]` ปลายเท้า → ข้อมือ (ทั้งคู่อยู่บนพื้น) |
| `lunge` | `flipped_points["front_toe_point"] − flipped_points["front_heel_point"]` เท้าหน้า |

**`build_normalization_matrix(exercise, flipped_points)`** คืน `(normalization_matrix, info)`

```
สูตร:   M = S · R(−θ) · Fx · T
โค้ด:   normalization_matrix = scaling_matrix @ rotation_matrix @ facing_reflection_matrix @ translation_matrix
```

เมทริกซ์ทางขวาสุดทำก่อน

| ลำดับ | ตัวแปร (สัญลักษณ์) | ทำอะไร | วิธีหา |
|---|---|---|---|
| 1 | `translation_matrix` (T) | เลื่อนสะโพกมาที่ (0,0) | `translation(−x ของสะโพก, −y ของสะโพก)` |
| 2 | `facing_reflection_matrix` (Fx) | ถ้าคนหันซ้าย ให้สะท้อนเป็นหันขวา | `floor = floor_vector(exercise, flipped_points)`; ถ้า `floor[0] < 0` ใช้ `reflect_x()` ไม่งั้นใช้ `np.eye(3)` |
| 3 | `rotation_matrix` (R) | หมุนให้พื้นขนานแกน x | `reflected_floor = facing_reflection_matrix[:2, :2] @ floor` (แนวพื้นหลังสะท้อน); `cos_theta = reflected_floor[0] / norm(reflected_floor)`, `sin_theta = reflected_floor[1] / norm(reflected_floor)`; `rotation(cos_theta, −sin_theta)` |
| 4 | `scaling_matrix` (S) | ย่อขยายให้ลำตัวยาว 1 | `torso_length = norm(ไหล่ − สะโพก)`; `scaling(1 / torso_length)` |

เวกเตอร์หนึ่งหน่วยของแนวพื้น = `reflected_floor / |reflected_floor|` = (cos θ, sin θ) โดย θ คือมุมที่พื้นเอียงจากแกน x การหมุน −θ จึงทำให้พื้นกลับมาขนานแกน x

`info` ต้องมี key ครบ 9 ตัว: `"translation_matrix"`, `"facing_reflection_matrix"`, `"rotation_matrix"`, `"scaling_matrix"`, `"floor"` (ก่อนสะท้อน), `"cos"` (= `cos_theta`), `"sin"` (= `sin_theta`), `"theta"` (= `math.degrees(math.atan2(sin_theta, cos_theta))`), `"torso"` (= `torso_length`)

ถ้าแนวพื้นยาว 0 จะเกิด `ZeroDivisionError` ไม่ต้องดัก ปล่อยให้งาน D จัดการ

**ตัวอย่างตรวจมือ** (ตัวอย่างเดียวกับในข้อเสนอโครงงาน)

```
ไหล่(47,54)  สะโพก(40,30)  เข่า(56,42)  ข้อเท้า(60,20)  ส้นเท้า(59,13)  ปลายเท้า(71,22)

floor = ปลายเท้า − ส้นเท้า = (12, 9)   |floor| = 15   cos θ = 0.8   sin θ = 0.6   θ = 36.87°
torso_length = |ไหล่ − สะโพก| = |(7, 24)| = 25

normalization_matrix = [[ 0.032, 0.024, −2],      inverse_matrix = [[20, −15, 40],
                        [−0.024, 0.032,  0],                        [15,  20, 30],
                        [ 0,     0,      1]]                        [ 0,   0,  1]]

det = 0.0016 = 1/25²        สะโพกหลังแปลง = (0, 0)        ไหล่หลังแปลง = (0.8, 0.6)
```

ทดสอบ

```bash
python check.py normalize
```

## ส่วนที่ 3: พิมพ์ขั้นตอนคำนวณ

ใช้ตอนรัน `--explain` และตอนนำเสนอ เพื่อแสดงว่าโปรแกรมคำนวณตามทฤษฎีจริง

**`format_number(value)`** ถ้า `value` เป็น `np.ndarray` คืนข้อความ `"(0.8000, 0.6000)"` (ทศนิยม 4 ตำแหน่ง คั่นด้วย `, `) ถ้าเป็นตัวเลขเดี่ยวคืน `"0.8000"`

**`print_explain(image_points, result)`** รับ `result` (shared_structure ข้อ 8) เริ่มด้วย `np.set_printoptions(precision=4, suppress=True)` แล้วพิมพ์ 6 หัวข้อ

| หัวข้อ | พิมพ์อะไร | อ่านจาก |
|---|---|---|
| หัว | ชื่อท่าภาษาไทย | `EXERCISES[result["exercise"]]["thai_name"]` |
| 1 | จุดหลังกลับแกน y ทีละจุด | `result["flipped_points"]` |
| 2 | เวกเตอร์แนวพื้น, ความยาว, (ถ้าหันซ้ายบอกว่าสะท้อนด้วย Fx), (cos θ, sin θ), θ | `result["info"]` |
| 3 | ความยาวลำตัว, เมทริกซ์ T, Fx (เฉพาะตอนใช้), R(−θ), S, M, det(M), M⁻¹, ผลตรวจ `M·M⁻¹ = I` | `result["info"]`, `result["normalization_matrix"]`, `result["inverse_matrix"]`, `determinant_3x3`, `np.allclose` |
| 4 | จุดหลัง normalize ทีละจุด | `result["normalized_points"]` |
| 5 | มุมทีละค่า (ชื่อไทย = ค่า°) แล้วต่อด้วยค่าประกอบ | `result["angle_values"]`, `EXERCISES[...]["angles"]`, `result["extra"]` |
| 6 | ระยะถึงท่าต้นแบบแต่ละ label: Euclidean, Manhattan, Cosine (ถ้า `result["from_file"]` เป็น False ให้เขียนกำกับว่า "ค่าสมมติ") | `result["ranking"]`, `EXERCISES[...]["labels"]` |

ในข้อความที่พิมพ์ใช้สัญลักษณ์ของสูตร (T, R, S, M) ได้ เพราะเป็นการแสดงสูตร ส่วนชื่อตัวแปรในโค้ดให้ใช้ชื่อเต็ม

รูปแบบการจัดบรรทัดเลือกเองได้ ขอให้อ่านแล้วไล่ตามการคำนวณได้ทีละขั้น

ทดสอบ: หลังงาน C merge แล้ว รัน `python selftest.py` ข้อ (ก) จะเรียก `print_explain` ตัวเลขต้องตรงกับตัวอย่างตรวจมือข้างบน

## เสร็จเมื่อ

- [ ] `python check.py matrix` ผ่าน 10/10
- [ ] `python check.py normalize` ผ่าน 8/8
- [ ] `print_explain` พิมพ์ครบ 6 หัวข้อ
- [ ] เปิด pull request และ merge เข้า `main`

## คำถามที่อาจารย์อาจถาม (เตรียมตอบ)

- ทำไมใช้เมทริกซ์ 3×3 กับจุด 2 มิติ
- ทำไมลำดับเป็น S·R·F·T สลับลำดับแล้วผลเปลี่ยนไหม (การคูณเมทริกซ์ไม่สลับที่)
- det(M) บอกอะไร (≠ 0 หา inverse ได้, ค่า = 1/torso_length² คืออัตราส่วนพื้นที่)
- Gauss-Jordan ต่างจาก Gaussian elimination ยังไง ทำไมต้องสลับแถว
