# โครงสร้างข้อมูลและระบบพิกัดของโปรแกรม

## 1. ชื่อข้อต่อ

ชื่อข้อต่อลงท้ายด้วย `_point` เพื่อแยกจากชื่อมุม (เช่น `knee_point` คือจุดเข่า ส่วน `knee` คือมุมเข่า) ระบบใช้ 8 ข้อต่อของแต่ละข้าง

| ชื่อ | ข้อต่อ | เลขจุด MediaPipe (ซ้าย/ขวา) | ใช้ในท่า |
|---|---|---|---|
| `shoulder_point` | ไหล่ | 11 / 12 | ทุกท่า |
| `elbow_point` | ศอก | 13 / 14 | Push-up |
| `wrist_point` | ข้อมือ | 15 / 16 | Push-up |
| `hip_point` | สะโพก | 23 / 24 | ทุกท่า |
| `knee_point` | เข่า | 25 / 26 | ทุกท่า |
| `ankle_point` | ข้อเท้า | 27 / 28 | ทุกท่า |
| `heel_point` | ส้นเท้า | 29 / 30 | Squat, Lunge |
| `toe_point` | ปลายเท้า | 31 / 32 | ทุกท่า |

ท่า Lunge ใช้ขาสองข้าง ก่อนแยกขาตั้งชื่อเป็น `left_…` และ `right_…` หลังแยกขา (`prepare_points`) เป็น `front_…` (ขาหน้า) และ `back_…` (ขาหลัง)

## 2. ระบบพิกัด 3 แบบ

| ตัวแปร | ระบบพิกัด | ลักษณะ | สัญลักษณ์ |
|---|---|---|---|
| `image_points` | พิกัดภาพ | หน่วยพิกเซล จุด (0, 0) อยู่มุมบนซ้าย y ชี้ลง | P_img |
| `flipped_points` | พิกัดคณิตศาสตร์ | กลับแกน y ให้ชี้ขึ้น | P |
| `normalized_points` | พิกัดมาตรฐาน | สะโพกอยู่ที่ (0, 0) พื้นขนานแกน x หันไปทาง +x ลำตัวยาว 1 | Q |

```
P     = Fy · P_img         กลับแกน y ของพิกัดภาพ
Q     = M · P              จัดท่าให้เป็นมาตรฐาน  โดย M = S · R(−θ) · Fx · T
x     = f(Q), x ∈ ℝ³       มุม 3 ค่า
P_img = Fy · M⁻¹ · Q       แปลงเส้นท่าที่ถูกกลับไปวาดบนภาพ
```

| ตัวแปรในโค้ด | สัญลักษณ์ | ทำอะไร |
|---|---|---|
| `flip_y_matrix` | Fy | กลับแกน y ของภาพ |
| `translation_matrix` | T | เลื่อนสะโพกไปที่ (0, 0) |
| `facing_reflection_matrix` | Fx | พลิกซ้าย-ขวา ใช้เมื่อผู้ใช้หันซ้าย |
| `rotation_matrix` | R(−θ) | หมุนให้พื้นขนานแกน x |
| `scaling_matrix` | S | ย่อขยายให้ลำตัวยาว 1 |
| `normalization_matrix` | M | S · R(−θ) · Fx · T |
| `inverse_matrix` | M⁻¹ | แปลงกลับจากพิกัดมาตรฐาน |
| `vertical_unit_vector` | e₂ | เวกเตอร์หนึ่งหน่วยแนวตั้ง (0, 1) |

## 3. มุมและแบบของแต่ละท่า

| ท่า | มุมที่ 1 | มุมที่ 2 | มุมที่ 3 | แบบ (ปุ่ม 1 / 2 / 3) |
|---|---|---|---|---|
| Squat | `knee` มุมเข่า | `hip` มุมสะโพก | `lean` มุมโน้มตัวจากแนวตั้ง | `correct` / `lean_forward` / `shallow` |
| Push-up | `elbow` มุมศอก | `hip_deviation` สะโพกเบี่ยง (+ โด่ง, − ตก) | `tilt` มุมลำตัวกับพื้น | `correct` / `shallow` / `hip_sag` |
| Lunge | `front_knee` มุมเข่าหน้า | `shin` มุมหน้าแข้ง (+ เข่าล้ำไปข้างหน้า) | `lean` มุมโน้มตัวจากแนวตั้ง | `correct` / `knee_over_toe` / `torso_lean` |

มุมทุกค่าเป็นองศา

## 4. การตั้งค่าแต่ละท่าใน config.py (`EXERCISES`)

| key | ค่า |
|---|---|
| `thai_name` | ชื่อท่าภาษาไทย |
| `angles` | มุม 3 ค่า พร้อมชื่อไทย และข้อความคำแนะนำเมื่อมุมมากกว่าหรือน้อยกว่าท่าถูก (ข้อความว่าง = ไม่มีคำแนะนำ) |
| `templates` | ท่าต้นแบบค่าสมมติ ใช้เมื่อยังไม่มี `templates.json` |
| `labels` | ชื่อแบบภาษาไทย |
| `gate` | เงื่อนไขว่าลงท่าแล้ว (ใช้ในโหมดกล้อง) |
| `lines` | คู่ข้อต่อที่ลากเส้นโครงร่าง |

ค่าคงที่อื่น: `TOLERANCE = 10.0` (มุมต่างจากท่าถูกได้ไม่เกิน ±10°), `VISIBILITY_MIN = 0.5` (เกณฑ์มองเห็นข้อต่อชัด)

## 5. ผลการวิเคราะห์ `result` (คืนจาก `analyze`)

| key | ค่า | ใช้ที่ |
|---|---|---|
| `exercise` | ชื่อท่า | วาดเส้นโครงร่าง |
| `angle_values` | มุม 3 ค่า | เขียนบนภาพ, บันทึก CSV, เช็กว่าลงท่าแล้ว |
| `ranking` | ระยะไปท่าต้นแบบทุกแบบ (Euclidean, Manhattan, Cosine) เรียงจาก Euclidean น้อยไปมาก `ranking[0]` คือผลการตรวจ | เลือกสีเส้น, แสดงระยะ |
| `checks` | ผลต่างจากท่าถูกและผ่าน/ไม่ผ่านทีละมุม | พิมพ์ผล |
| `tips` | ข้อความคำแนะนำ | พิมพ์ผล |
| `ghosts` | เส้นท่าที่ถูกในพิกัดภาพ | วาดเส้นเหลือง |
| `normalization_matrix`, `inverse_matrix`, `info`, `flipped_points`, `normalized_points`, `extra` | ค่าระหว่างทาง | `--explain`, ชุดทดสอบ |
| `from_file` | ท่าต้นแบบมาจาก `templates.json` หรือไม่ | พิมพ์ผล |

## 6. สถานะของภาพ

`ok` ใช้ได้ / `unreadable` เปิดไฟล์ไม่ได้ / `no_person` ไม่พบคน / `low_visibility` เห็นข้อต่อไม่ชัด / `calc_error` คำนวณไม่ได้

## 7. ไฟล์ข้อมูล

**`data_<ท่า>.csv`** 1 แถว = 1 ภาพ รวม 106 คอลัมน์

| คอลัมน์ | จำนวน | ค่า |
|---|---|---|
| `time`, `exercise`, `label`, `side` | 4 | เวลา ชื่อท่า แบบ และข้างที่ใช้ |
| ชื่อมุม 3 ตัว เช่น `knee`, `hip`, `lean` | 3 | เวกเตอร์มุม (องศา) |
| `x0`, `y0`, …, `x32`, `y32` | 66 | พิกัด 33 จุดจาก MediaPipe (สัดส่วน 0–1 ของภาพ) |
| `v0`, …, `v32` | 33 | visibility ของแต่ละจุด |

**`clean_log.csv`** 1 แถวต่อ 1 ภาพที่ป้อนตอนเก็บข้อมูล: `time, exercise, label, image, status`

**`templates.json`** ท่าต้นแบบจากข้อมูลจริง (ค่าเฉลี่ยของแต่ละแบบ)

```json
{"squat":  {"correct": [76.49, 72.29, 27.56], "lean_forward": [76.65, 51.46, 42.13], "shallow": [103.03, 103.25, 20.1]},
 "pushup": {"correct": [75.06, -0.52, 3.82], "shallow": [135.21, -3.06, 14.15], "hip_sag": [88.98, -20.66, 8.75]},
 "lunge":  {"correct": [79.62, 7.25, 4.54], "knee_over_toe": [75.26, 19.41, 4.38], "torso_lean": [85.49, 0.25, 21.26]}}
```

## 8. การเรียกใช้ระหว่างไฟล์

A ← B หมายถึง B import ฟังก์ชันจาก A (`check.py` import `vector`, `matrix`, `angles` ภายในฟังก์ชันทดสอบแต่ละชุด)

```
config.py   ← matrix.py, analyze.py, dataset.py, capture.py, pose_coach.py, selftest.py
vector.py   ← matrix.py, angles.py, analyze.py, dataset.py
matrix.py   ← analyze.py, selftest.py
angles.py   ← analyze.py, capture.py, selftest.py
analyze.py  ← capture.py, selftest.py
capture.py, dataset.py, selftest.py ← pose_coach.py
```

## 9. ชุดทดสอบ

| คำสั่ง | ทดสอบอะไร |
|---|---|
| `python check.py vector` | ฟังก์ชันเวกเตอร์ เช่น \|(3, 4)\| = 5, projection, cross product, ระยะ |
| `python check.py matrix` | เมทริกซ์การแปลง, det และ M⁻¹ เทียบกับ NumPy, เมทริกซ์เอกฐานต้องแจ้ง error |
| `python check.py normalize` | M, det = 0.0016 และ M⁻¹ ของตัวอย่าง, ผู้ใช้หันซ้ายต้องได้พิกัดมาตรฐานเท่าเดิม |
| `python check.py angles` | มุมของทั้ง 3 ท่า, การเลือกขาหน้า, เส้นท่าที่ถูก |
| `python pose_coach.py --selftest` | ทั้งระบบ: ตัวอย่างคำนวณด้วยมือ, ท่า Push-up และ Lunge ที่รู้คำตอบ ถ่ายจากมุมกล้องสุ่ม 50 ครั้งต้องได้มุมเท่าเดิม, สะโพกตก, Gauss-Jordan เทียบ NumPy |
