# งาน B: เวกเตอร์

ไฟล์: `posecoach/vector.py`, `posecoach/angles.py` | ส่งภายใน **6 ต.ค. 69** | ทฤษฎี: บท 1, 2

อ่าน [shared_structure.md](shared_structure.md) ข้อ 1-4 ก่อน

งานนี้ส่งเป็นงานแรก เพราะทุกไฟล์เรียกใช้ `vector.py` ถ้าทำ `vector.py` เสร็จก่อน ให้เปิด pull request ส่วนนั้นก่อนได้เลย

## งานนี้ทำอะไร

แปลงจุดข้อต่อ (ที่ normalize แล้ว) ให้เป็นมุม 3 ค่าต่อท่า ด้วย dot product, projection และ cross product และเตรียมฟังก์ชันวัดระยะทางให้งาน C ใช้เทียบท่าต้นแบบ

ห้ามใช้ `np.linalg.norm` (ใช้ `@` หรือ `np.dot` หา dot product ได้)

## ส่วนที่ 1: `vector.py`

| ฟังก์ชัน | สูตร | คืน |
|---|---|---|
| `norm(vector)` | \|v\| = √(v · v) | float |
| `angle_between(first_vector, second_vector)` | cos φ = (u · v) / (\|u\| \|v\|) → φ = arccos | องศา 0-180 |
| `angle_at(center_point, first_point, second_point)` | มุมระหว่าง `first_point − center_point` กับ `second_point − center_point` | องศา |
| `projection(vector, base_vector)` | component = (t · b) / \|b\|, projected = ((t · b) / (b · b)) b, perpendicular = t − projected | `(component, projected, perpendicular)` |
| `cross_z(first_vector, second_vector)` | u₀v₁ − u₁v₀ | float |
| `euclidean(first_vector, second_vector)` | \|a − b\| | float |
| `manhattan(first_vector, second_vector)` | Σ \|aᵢ − bᵢ\| | float |
| `cosine(first_vector, second_vector)` | (a · b) / (\|a\| \|b\|) | float |
| `signed_from_vertical(vector)` | ดูด้านล่าง | องศา −180 ถึง 180 |

ชื่อ 3 ค่าที่ `projection` คืน ตรงกับสัญลักษณ์ในสไลด์ดังนี้: `component` = comp (ความยาวของเงา), `projected` = proj (เวกเตอร์เงา), `perpendicular` = ส่วนตั้งฉาก

ต้นไฟล์มี `vertical_unit_vector = (0, 1)` คือเวกเตอร์หนึ่งหน่วยแนวตั้ง ĵ ใช้วัดว่าเวกเตอร์เอียงจากแนวตั้งกี่องศา

ข้อควรระวัง

- **`angle_between`**: ค่า cos ที่คำนวณได้อาจเกินช่วงเล็กน้อยจากการปัดเศษ เช่น 1.0000000002 ทำให้ `math.acos` error ต้องบีบให้อยู่ใน [−1, 1] ก่อน: `max(-1.0, min(1.0, cosine_value))`
- **`angle_at`**: เวกเตอร์สองตัวต้องเริ่มจากข้อต่อ `center_point` ทั้งคู่ ถ้าลบกลับด้านจะได้มุมผิด
- ตัวแปรที่เก็บค่า cos ให้ชื่อ `cosine_value` (ไม่ใช้ `cosine` เพราะซ้ำกับชื่อฟังก์ชัน)
- ค่าที่คืนเป็นตัวเลขเดี่ยวให้ครอบด้วย `float(...)` จะได้ไม่ติดชนิด `np.float64` ตอนพิมพ์

**`signed_from_vertical(vector)`** มุมที่ `vector` เอียงจากแนวตั้ง มีเครื่องหมาย

1. `component, _, perpendicular = projection(vector, vertical_unit_vector)`
2. `angle = arccos(component / |vector|)` เป็นองศา (บีบค่าให้อยู่ใน [−1, 1] ก่อนเหมือนกัน)
3. ถ้า `perpendicular[0] >= 0` (เอียงไปทาง +x = ข้างหน้า) คืน `angle` ไม่งั้นคืน `−angle`

`component` คือความยาวของ `vector` ในแนวตั้ง, `perpendicular` คือส่วนที่เหลือในแนวนอน เครื่องหมายของ `perpendicular` บอกว่าเอียงไปทางไหน

ทดสอบ

```bash
python check.py vector
```

## ส่วนที่ 2: `angles.py`

### `prepare_points(exercise, points)`

ท่าที่ไม่ใช่ `lunge` คืน `points` ตัวเดิม

ท่า `lunge` ต้องแยกว่าขาไหนเป็นขาหน้า (ชื่อ key ดู shared_structure ข้อ 1)

1. ทิศที่คนหัน: `facing = (left_toe_point − left_heel_point) + (right_toe_point − right_heel_point)` (รวมเวกเตอร์ส้น → ปลายเท้าของสองเท้า)
2. `direction_sign = 1.0` ถ้า `facing[0] >= 0` ไม่งั้น `−1.0`
3. ขาหน้า = ข้างที่ข้อเท้าอยู่ไปทางทิศนั้นมากกว่า: ถ้า `direction_sign × x ของ left_ankle_point >= direction_sign × x ของ right_ankle_point` แล้ว `front_side = 'left'`, `back_side = 'right'` ไม่งั้นสลับกัน
4. สร้าง dict ใหม่: `shoulder_point`, `hip_point` ค่าเดิม และ `front_knee_point` `front_ankle_point` `front_heel_point` `front_toe_point` จากขาหน้า, `back_…` จากขาหลัง

### `compute_angles(exercise, normalized_points)`

`normalized_points` อยู่ในพิกัดมาตรฐานแล้ว (หันไปทาง +x, y ชี้ขึ้น) คืน `(angle_values, extra)` โดย `angle_values` เป็น `np.array` 3 ค่า

ดึงจุดออกมาใส่ตัวแปรชื่อเดียวกับ key ก่อนใช้ เช่น `knee_point = normalized_points['knee_point']` (ต้องมี `_point` เพราะ `knee` เป็นชื่อมุม ถ้าใช้ชื่อซ้ำกันค่าจะทับกัน)

**squat**

| ค่า | วิธีคำนวณ |
|---|---|
| `knee` | `angle_at(knee_point, hip_point, ankle_point)` |
| `hip` | `angle_at(hip_point, shoulder_point, knee_point)` |
| `lean` | `torso_vector = shoulder_point − hip_point`; `component, projected, perpendicular = projection(torso_vector, vertical_unit_vector)`; `lean = arccos(component / |torso_vector|)` องศา (บีบ [−1, 1]) |

`extra` = `{"torso_vector": torso_vector, "component บน ĵ": component, "projection บน ĵ": projected, "ส่วนตั้งฉาก": perpendicular, "เข่าเลยปลายเท้า (เท่าลำตัว)": x ของ knee_point − x ของ toe_point}`

**pushup**

| ค่า | วิธีคำนวณ |
|---|---|
| `elbow` | `angle_at(elbow_point, shoulder_point, wrist_point)` |
| `hip_deviation` | `body_angle = angle_at(hip_point, shoulder_point, ankle_point)`; `body_line = shoulder_point − ankle_point`; `cross_value = cross_z(body_line, hip_point − ankle_point)`; `hip_deviation = (180 − body_angle)` คูณ `+1` ถ้า `cross_value >= 0` ไม่งั้น `−1` |
| `tilt` | `angle_between(body_line, (1, 0))` |

ลำตัวตรง → `body_angle` = 180° → `hip_deviation` = 0 ส่วน cross product บอกว่าสะโพกอยู่ฝั่งไหนของเส้นข้อเท้า → ไหล่: `cross_value` บวก = อยู่เหนือเส้น (โด่ง), ลบ = อยู่ใต้เส้น (ตก) dot product อย่างเดียวบอกได้แค่ขนาดมุม บอกทิศไม่ได้ จึงต้องใช้ cross product

`extra` = `{"มุมลำตัวที่สะโพก": body_angle, "cross product (z)": cross_value, "ระยะสะโพกจากเส้น ไหล่-ข้อเท้า": perpendicular}` โดย `perpendicular` มาจาก `projection(hip_point − ankle_point, body_line)`

**lunge**

| ค่า | วิธีคำนวณ |
|---|---|
| `front_knee` | `angle_at(front_knee_point, hip_point, front_ankle_point)` |
| `shin` | `signed_from_vertical(front_knee_point − front_ankle_point)` |
| `lean` | `abs(signed_from_vertical(shoulder_point − hip_point))` |

`extra` = `{"มุมเข่าหลัง": angle_at(back_knee_point, hip_point, back_ankle_point), "เข่าหน้าเลยปลายเท้า (เท่าลำตัว)": x ของ front_knee_point − x ของ front_toe_point}`

**ตัวอย่างตรวจมือ (squat)**

```
normalized_points:  ไหล่(0.8, 0.6)  สะโพก(0, 0)  เข่า(0.8, 0)  ข้อเท้า(0.4, −0.8)

knee: เข่า→สะโพก = (−0.8, 0), เข่า→ข้อเท้า = (−0.4, −0.8)   cos = 0.32 / (0.8 × 0.8944) = 0.4472   → 63.43°
hip : สะโพก→ไหล่ = (0.8, 0.6), สะโพก→เข่า = (0.8, 0)        cos = 0.64 / (1 × 0.8)      = 0.8      → 36.87°
lean: torso_vector = (0.8, 0.6), component = 0.6, ความยาว = 1                            cos = 0.6  → 53.13°
```

### `ghost_segments(exercise, normalized_points, correct_template)`

คืน list ของ `(จุดเริ่ม, จุดปลาย)` เป็นเส้นของท่าที่ถูก ในพิกัดมาตรฐาน (งาน C จะแปลงกลับไปพิกัดภาพด้วย `inverse_matrix`) `correct_template` = มุม 3 ค่าของท่าต้นแบบ `correct`

เวกเตอร์หนึ่งหน่วยที่เอียงจากแนวตั้งไปข้างหน้า α องศา คือ `(sin α, cos α)`

| ท่า | เส้น |
|---|---|
| `squat` | 1 เส้น: จาก `hip_point` ไป `hip_point + torso_direction` โดย `torso_direction = (sin, cos)` ของ `lean_angle = correct_template[2]` (มุมโน้มตัวที่ถูก, ลำตัวยาว 1) |
| `pushup` | 2 เส้น: `body_line = shoulder_point − ankle_point`; `projected` = projection ของ `hip_point − ankle_point` บน `body_line`; สะโพกที่ถูก `correct_hip_point = ankle_point + projected` (จุดบนเส้นไหล่-ข้อเท้าที่ใกล้สะโพกจริงที่สุด) → `(shoulder_point, correct_hip_point)` และ `(correct_hip_point, ankle_point)` |
| `lunge` | 2 เส้น: หน้าแข้งที่ถูก จาก `front_ankle_point` ไป `front_ankle_point + correct_shin_vector` โดย `correct_shin_vector = ความยาวหน้าแข้งจริง × (sin, cos)` ของ `shin_angle = correct_template[1]`; ลำตัวที่ถูก จาก `hip_point` ไป `hip_point + lean_direction` โดย `lean_direction = (sin, cos)` ของ `lean_angle = correct_template[2]` |

ความยาวหน้าแข้งจริง = `norm(front_knee_point − front_ankle_point)` ต้องคูณเข้าไป ไม่งั้นเส้นจะยาวเท่าลำตัวและเลยเข่า

อย่าลืมแปลงองศาเป็นเรเดียน (`math.radians`) ก่อนเข้า `math.sin` / `math.cos`

ทดสอบ

```bash
python check.py angles
```

## เสร็จเมื่อ

- [ ] `python check.py vector` ผ่าน 10/10
- [ ] `python check.py angles` ผ่าน 11/11
- [ ] เปิด pull request และ merge เข้า `main`

## คำถามที่อาจารย์อาจถาม (เตรียมตอบ)

- หามุมจาก dot product ยังไง ทำไมต้องลบด้วยจุดข้อต่อก่อน
- comp กับ proj ต่างกันยังไง ใช้ตรงไหนในโครงงาน
- ทำไมท่าวิดพื้นต้องใช้ cross product เพิ่ม
- Euclidean, Manhattan, Cosine ต่างกันยังไง ทำไมเลือก Euclidean ตัดสิน
