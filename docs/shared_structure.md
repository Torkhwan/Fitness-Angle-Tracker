# โครงสร้างที่ใช้ร่วมกัน

ทุกคนอ่านก่อนเริ่มเขียน ชื่อและรูปแบบในหน้านี้ต้องใช้ตรงกันทุกไฟล์

## 1. ชื่อข้อต่อ

ชื่อข้อต่อทุกตัวลงท้ายด้วย `_point` เพื่อแยกจากชื่อมุม (เช่น `knee_point` คือจุดเข่า ส่วน `knee` คือมุมเข่า)

| ชื่อ | ข้อต่อ | | ชื่อ | ข้อต่อ |
|---|---|---|---|---|
| `shoulder_point` | ไหล่ | | `knee_point` | เข่า |
| `elbow_point` | ศอก | | `ankle_point` | ข้อเท้า |
| `wrist_point` | ข้อมือ | | `heel_point` | ส้นเท้า |
| `hip_point` | สะโพก | | `toe_point` | ปลายเท้า |

ท่า lunge ใช้ขาสองข้าง จึงมีคำนำหน้า

- ก่อนแยกขา: `left_knee_point` `left_ankle_point` `left_heel_point` `left_toe_point` (ซ้าย) และ `right_knee_point` `right_ankle_point` `right_heel_point` `right_toe_point` (ขวา)
- หลังแยกขา (`prepare_points`): `front_knee_point` `front_ankle_point` `front_heel_point` `front_toe_point` (ขาหน้า) และ `back_knee_point` `back_ankle_point` `back_heel_point` `back_toe_point` (ขาหลัง)

เลขดัชนีของ MediaPipe อยู่ใน `config.LANDMARK_INDEX` เช่น `LANDMARK_INDEX["left"]["knee_point"]` = 25
ข้อต่อที่แต่ละท่าต้องเห็นอยู่ใน `config.REQUIRED_POINTS`

## 2. ชนิดข้อมูล

| สิ่งที่เก็บ | รูปแบบ |
|---|---|
| จุด 1 จุด / เวกเตอร์ 2 มิติ | `np.array([x, y])` ชนิด float |
| กลุ่มจุด | `dict` ชื่อข้อต่อ → จุด เช่น `{"shoulder_point": np.array([47., 54.]), "hip_point": ...}` |
| เมทริกซ์การแปลง | `np.array` ขนาด 3×3 ชนิด float (homogeneous coordinates) |
| มุมของท่า (`angle_values`) | `np.array` 3 ค่า หน่วยองศา |
| มุมทุกค่า | **องศา** (ใช้เรเดียนเฉพาะตอนส่งเข้า `math.sin` / `math.cos`) |

## 3. ระบบพิกัด 3 แบบ และชื่อตัวแปร

| ตัวแปร | ระบบพิกัด | ลักษณะ | สัญลักษณ์ในสูตร |
|---|---|---|---|
| `image_points` / `points` | พิกัดภาพ | หน่วย pixel, จุด (0,0) อยู่มุมบนซ้าย, **y ชี้ลง** | |
| `flipped_points` | พิกัดคณิตศาสตร์ | กลับแกน y ของพิกัดภาพให้ **y ชี้ขึ้น** | P |
| `normalized_points` | พิกัดมาตรฐาน | สะโพกอยู่ที่ (0,0), พื้นขนานแกน x, หันหน้าไปทาง +x, ลำตัวยาว 1 | Q |

ลำดับการแปลง

```
image_points ──flip_y_matrix──► flipped_points ──normalization_matrix──► normalized_points ──► angle_values
                                                                               │
ภาพ ◄──flip_y_matrix── ◄──inverse_matrix── เส้นท่าที่ถูก (คำนวณในพิกัดมาตรฐาน)
```

ชื่อเมทริกซ์ในโค้ดกับสัญลักษณ์ในสูตร

| ตัวแปรในโค้ด | สัญลักษณ์ | ทำอะไร |
|---|---|---|
| `flip_y_matrix` | Fy | กลับแกน y ของภาพ |
| `translation_matrix` | T | เลื่อนสะโพกไปที่ (0, 0) |
| `facing_reflection_matrix` | Fx | สะท้อนซ้าย-ขวา ใช้เฉพาะตอนคนหันซ้าย |
| `rotation_matrix` | R(−θ) | หมุนให้พื้นขนานแกน x |
| `scaling_matrix` | S | ย่อขยายให้ลำตัวยาว 1 |
| `normalization_matrix` | M | `scaling_matrix @ rotation_matrix @ facing_reflection_matrix @ translation_matrix` |
| `inverse_matrix` | M⁻¹ | แปลงกลับจากพิกัดมาตรฐาน |
| `vertical_unit_vector` | ĵ | เวกเตอร์หนึ่งหน่วยแนวตั้ง (0, 1) |

สูตรเต็ม: M = S · R(−θ) · [Fx] · T

## 4. มุมของแต่ละท่า

ลำดับใน `angle_values` ต้องตรงกับ `EXERCISES[exercise]["angles"]` เสมอ

| ท่า | `angle_values[0]` | `angle_values[1]` | `angle_values[2]` |
|---|---|---|---|
| `squat` | `knee` มุมเข่า | `hip` มุมสะโพก | `lean` มุมลำตัวจากแนวตั้ง |
| `pushup` | `elbow` มุมศอก | `hip_deviation` สะโพกเบี่ยงจากแนวลำตัว (+ โด่ง, − ตก) | `tilt` มุมลำตัวกับพื้น |
| `lunge` | `front_knee` มุมเข่าหน้า | `shin` มุมหน้าแข้งหน้าจากแนวตั้ง (+ เข่าล้ำไปข้างหน้า) | `lean` มุมลำตัวจากแนวตั้ง |

## 5. label ของแต่ละท่า

| ท่า | ปุ่ม 1 | ปุ่ม 2 | ปุ่ม 3 |
|---|---|---|---|
| `squat` | `correct` | `lean_forward` | `shallow` |
| `pushup` | `correct` | `shallow` | `hip_sag` |
| `lunge` | `correct` | `knee_over_toe` | `torso_lean` |

## 6. `EXERCISES[exercise]` ใน config.py

| key | ค่า |
|---|---|
| `"thai_name"` | ชื่อท่าภาษาไทย |
| `"angles"` | list ของ `(ชื่อ, ชื่อไทย, ข้อความเมื่อมากกว่าท่าถูก, ข้อความเมื่อน้อยกว่าท่าถูก)` ข้อความว่าง `""` = ไม่ต้องเตือน, ในข้อความมี `{difference:.0f}` ไว้ใส่จำนวนองศาที่ต่าง |
| `"templates"` | ท่าต้นแบบค่าสมมติ `{label: [มุม 3 ค่า]}` ใช้เมื่อยังไม่มี `templates.json` |
| `"labels"` | `{label: ข้อความไทย}` |
| `"gate"` | ฟังก์ชันรับ `angle_values` คืน True เมื่ออยู่ในช่วงลงท่า (ใช้กับกล้อง) |
| `"lines"` | คู่ชื่อข้อต่อที่ลากเส้นโครงร่าง |

## 7. `info` (คืนจาก `build_normalization_matrix`)

| key | ค่า |
|---|---|
| `"translation_matrix"` `"facing_reflection_matrix"` `"rotation_matrix"` `"scaling_matrix"` | เมทริกซ์ 3×3 แต่ละตัวที่ประกอบเป็น `normalization_matrix` (`facing_reflection_matrix` เป็นเมทริกซ์เอกลักษณ์ถ้าคนหันขวาอยู่แล้ว) |
| `"floor"` | เวกเตอร์แนวพื้น (ก่อนสะท้อน) |
| `"cos"` `"sin"` | cos θ, sin θ ของแนวพื้นหลังสะท้อน |
| `"theta"` | θ เป็นองศา |
| `"torso"` | ความยาวลำตัว \|ไหล่ − สะโพก\| |

## 8. `result` (คืนจาก `analyze`)

งาน A (`print_explain`) และงาน D (`draw`, `save_row`) อ่านค่าจาก dict นี้ งาน C เป็นคนสร้าง

| key | ค่า |
|---|---|
| `"exercise"` | ชื่อท่า |
| `"angle_values"` | มุม 3 ค่า |
| `"ranking"` | list ของ `{"name", "euclidean", "manhattan", "cosine"}` เรียงจาก Euclidean น้อยไปมาก → `result["ranking"][0]["name"]` คือ label ที่ระบบทาย |
| `"checks"` | list ของ `(ชื่อไทย, ผลต่างจากท่าถูก, ผ่านไหม)` ต่อ 1 มุม |
| `"tips"` | list ข้อความคำแนะนำ |
| `"normalization_matrix"` `"inverse_matrix"` | เมทริกซ์ normalize และ inverse |
| `"info"` | ข้อ 7 |
| `"flipped_points"` `"normalized_points"` | จุดในพิกัดคณิตศาสตร์ / พิกัดมาตรฐาน |
| `"extra"` | ค่าประกอบจาก `compute_angles` (ใช้พิมพ์ตอน explain) |
| `"ghosts"` | list ของ `(จุดเริ่ม, จุดปลาย)` เส้นท่าที่ถูก **ในพิกัดภาพ** พร้อมวาด |
| `"from_file"` | True = ท่าต้นแบบมาจาก `templates.json` |

## 9. สถานะของภาพ

`"ok"` ใช้ได้ / `"unreadable"` เปิดไฟล์ไม่ได้ / `"no_person"` ไม่พบคน / `"low_visibility"` เห็นข้อต่อไม่ชัด / `"calc_error"` คำนวณไม่ได้

ข้อความไทยของแต่ละสถานะอยู่ใน `config.SKIP_REASON`

## 10. ไฟล์ข้อมูล

**`data_<ท่า>.csv`** 1 แถว = 1 ภาพ (งาน D เขียน, งาน C อ่าน)

| คอลัมน์ | จำนวน | ค่า |
|---|---|---|
| `time` | 1 | `YYYY-MM-DD HH:MM:SS` |
| `exercise` `label` `side` | 3 | ชื่อท่า, label, `left`/`right` |
| ชื่อมุม 3 ตัว | 3 | เช่น `knee` `hip` `lean` ทศนิยม 3 ตำแหน่ง |
| `x0` `y0` `x1` `y1` … `x32` `y32` | 66 | พิกัด 33 จุดจาก MediaPipe (ค่า 0-1) ทศนิยม 5 ตำแหน่ง |
| `v0` … `v32` | 33 | visibility ของแต่ละจุด ทศนิยม 3 ตำแหน่ง |

**`clean_log.csv`** 1 แถว = 1 ภาพที่ป้อนตอนเก็บข้อมูล: `time, exercise, label, image, status`

**`templates.json`** ท่าต้นแบบจากข้อมูลจริง

```json
{"squat": {"correct": [65.2, 55.1, 35.4], "lean_forward": [...], "shallow": [...]},
 "pushup": {...}, "lunge": {...}}
```

## 11. การ import

```
config.py   ← ทุกไฟล์
vector.py   ← matrix.py, angles.py, analyze.py, dataset.py
matrix.py   ← analyze.py
angles.py   ← analyze.py, capture.py
analyze.py  ← capture.py
capture.py, dataset.py ← pose_coach.py
```

บรรทัด import เขียนไว้ให้ครบทุกไฟล์แล้ว ถ้าต้อง import เพิ่มให้ดูว่าไม่วนกลับ (เช่น `vector.py` ห้าม import `matrix.py`)

## 12. รูปแบบโค้ด

- **ตั้งชื่อเป็นคำเต็ม ไม่ใช้ตัวย่อ** เช่น `exercise` ไม่ใช่ `ex`, `points` ไม่ใช่ `pts`, `result` ไม่ใช่ `r`
- ชื่อฟังก์ชันและตัวแปรเป็นภาษาอังกฤษตัวเล็ก คั่นด้วย `_` ค่าคงที่ใน `config.py` เป็นตัวพิมพ์ใหญ่
- ชื่อข้อต่อลงท้ายด้วย `_point` ทั้งใน dict และตัวแปร เช่น `knee_point = normalized_points["knee_point"]`
- ยกเว้นที่คงไว้: `a` ถึง `i` ในสูตร determinant, `_` สำหรับค่าที่ไม่ใช้, ศัพท์คณิตศาสตร์ `norm` `cos` `sin` `theta`
- comment และข้อความที่พิมพ์ออกหน้าจอเป็นภาษาไทย
- ค่าคงที่ทุกตัวอ่านจาก `config.py` ไม่พิมพ์ตัวเลขซ้ำในไฟล์ตัวเอง
- เว้นวรรค 4 ช่อง, บรรทัดไม่เกิน ~120 ตัวอักษร
