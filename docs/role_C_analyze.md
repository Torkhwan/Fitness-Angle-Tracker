# งาน C: วิเคราะห์ผล

ไฟล์: `posecoach/analyze.py` ส่งภายใน **8 ต.ค. 69** | `posecoach/dataset.py` ส่งภายใน **11 ต.ค. 69**

อ่าน [shared_structure.md](shared_structure.md) ทั้งหน้า โดยเฉพาะข้อ 6, 8, 10

## งานนี้ทำอะไร

- `analyze.py` ต่อฟังก์ชันของงาน A และ B เข้าด้วยกันเป็นสายเดียว: พิกัดภาพ → normalize → มุม 3 ค่า → เทียบท่าต้นแบบ → คำแนะนำ
- `dataset.py` อ่านข้อมูลที่เก็บมา clean ทำสถิติสำหรับรายงาน สร้างท่าต้นแบบจากค่าเฉลี่ย และวัดความแม่นยำ

## ส่วนที่ 1: `analyze.py`

### `load_templates(exercise)`

คืน `(templates, from_file)` โดย `templates` = `{label: np.array 3 ค่า (float)}`

1. ถ้ามีไฟล์ `TEMPLATE_PATH` → เปิดด้วย `encoding="utf-8"` อ่านด้วย `json.load` เก็บใน `saved_templates` ถ้ามี key `exercise` → คืนค่าจากไฟล์กับ `True`
2. ไม่งั้นคืนค่าสมมติจาก `EXERCISES[exercise]["templates"]` กับ `False`

### `analyze(exercise, image_points, explain=False, templates=None)`

| ขั้น | ทำอะไร | ใช้ |
|---|---|---|
| 1 | `flip_y_matrix = reflect_y()`; `flipped_points` = ทุกจุดใน `image_points` ผ่าน `apply(flip_y_matrix, point)` | งาน A |
| 2 | `normalization_matrix, info = build_normalization_matrix(exercise, flipped_points)` | งาน A |
| 3 | `normalized_points` = ทุกจุดใน `flipped_points` ผ่าน `apply(normalization_matrix, point)` | งาน A |
| 4 | `angle_values, extra = compute_angles(exercise, normalized_points)` | งาน B |
| 5 | ถ้า `templates` เป็น None → `load_templates(exercise)` (ไม่งั้น `from_file = False`) | |
| 6 | `ranking`: ทุก label คำนวณระยะจาก `angle_values` ถึงท่าต้นแบบ แล้วเรียงตาม Euclidean น้อย → มาก | งาน B |
| 7 | `correct_template` = ท่าต้นแบบ `correct` (ถ้าไม่มี ใช้ตัวแรก); `difference = angle_values − correct_template` | |
| 8 | `checks` และ `tips` (ดูด้านล่าง) | |
| 9 | `inverse_matrix = gauss_jordan_inverse(normalization_matrix)` | งาน A |
| 10 | `ghosts`: ทุกเส้นจาก `ghost_segments(exercise, normalized_points, correct_template)` แปลงปลายทั้งสองกลับพิกัดภาพ | งาน A, B |
| 11 | รวมทุกอย่างเป็น dict `result` (key ครบตาม shared_structure ข้อ 8) | |
| 12 | ถ้า `explain` → `print_explain(image_points, result)` แล้วคืน `result` | งาน A |

**ขั้น 6: nearest template**

```
แต่ละ label ที่มีท่าต้นแบบ template:
    {"name": label, "euclidean": euclidean(angle_values, template),
     "manhattan": manhattan(angle_values, template), "cosine": cosine(angle_values, template)}
label ที่ระบบทาย = ตัวที่ "euclidean" น้อยที่สุด = ranking[0]
```

ตัดสินด้วย Euclidean เท่านั้น Manhattan กับ Cosine เก็บไว้พิมพ์เทียบในรายงาน

**ขั้น 8: checks และ tips** วนทุกมุมลำดับที่ `index` (`thai_name`, `message_when_higher`, `message_when_lower` มาจาก `EXERCISES[exercise]["angles"][index]`)

- `checks` เพิ่ม `(thai_name, difference[index], abs(difference[index]) <= TOLERANCE)`
- ถ้า `difference[index] > TOLERANCE` และ `message_when_higher` ไม่ว่าง → `tips` เพิ่ม `message_when_higher.format(difference=difference[index])`
- ถ้า `difference[index] < −TOLERANCE` และ `message_when_lower` ไม่ว่าง → `tips` เพิ่ม `message_when_lower.format(difference=−difference[index])`

**ขั้น 10: แปลงกลับ** จุด `point` ในพิกัดมาตรฐาน → พิกัดภาพ = `apply(flip_y_matrix, apply(inverse_matrix, point))`

`inverse_matrix` ย้อนการ normalize (พิกัดมาตรฐาน → พิกัดคณิตศาสตร์) แล้ว `flip_y_matrix` กลับแกน y อีกครั้ง (พิกัดคณิตศาสตร์ → ภาพ) เพราะการกลับแกน y เป็น inverse ของตัวเอง แต่ละเส้นเก็บเป็น tuple `(จุดเริ่ม, จุดปลาย)`

**ตัวอย่างตรวจมือ** (ท่าต้นแบบค่าสมมติของ squat)

```
angle_values = [63.43, 36.87, 53.13]
lean_forward = [65, 35, 55]   difference = (−1.57, 1.87, −1.87)   Euclidean = √(2.46 + 3.50 + 3.50) = 3.07   ← ใกล้ที่สุด
correct      = [65, 55, 35]   difference = (−1.57, −18.13, 18.13)  → มุมโน้มตัวเกิน 18° > TOLERANCE → มีคำแนะนำ
```

### `print_result(result)`

พิมพ์ตามลำดับ

1. `[ชื่อท่าไทย] มุม = ...` ทศนิยม 1 ตำแหน่ง
2. `ผล: ใกล้เคียง "<ข้อความไทยของ label ที่ทาย>" มากที่สุด` (ข้อความจาก `EXERCISES[exercise]["labels"]`)
3. แต่ละรายการใน `result["checks"]`: ชื่อไทย, ต่างจากท่าถูกกี่องศา (มีเครื่องหมาย + −), ผ่าน/ไม่ผ่าน
4. แต่ละรายการใน `result["tips"]`: `คำแนะนำ: ...`
5. ถ้า `result["from_file"]` เป็น False: เตือนว่ายังใช้ท่าต้นแบบค่าสมมติ ให้เก็บข้อมูลแล้วรัน `--build-templates`

ทดสอบ (ต้องมีงาน A และ B ใน `main` แล้ว กด Update from main ก่อน)

```bash
python selftest.py
```

ต้องขึ้น `SELFTEST: ผ่านทั้งหมด ✔`

## ส่วนที่ 2: `dataset.py`

รูปแบบไฟล์ CSV ดู shared_structure ข้อ 10 เปิดไฟล์ทุกครั้งใส่ `encoding="utf-8"`

### `load_dataset(paths)`

คืน `(groups, clean_counts)`

- `groups` = `{ท่า: {label: np.array ขนาด n×3}}` 1 แถว = มุม 3 ค่าของ 1 ภาพ
- `clean_counts` = `{ท่า: {"rows": .., "duplicate": .., "complete": .., "check": ..}}`

วนทุกไฟล์ อ่านด้วย `csv.DictReader` (ตัวแปร `reader`) ทุกแถว

1. ถ้าไฟล์ไม่มีคอลัมน์ `exercise` → `sys.exit` พร้อมข้อความบอกว่าเป็นรูปแบบเก่า
2. `rows` + 1
3. **แถวซ้ำ**: สร้าง `row_key` เป็น tuple ของพิกัด 66 ค่า (`x0, y0, …, x32, y32`) ถ้าเคยเจอแล้ว (เก็บใน set ชื่อ `seen_rows`) → `duplicate` + 1 แล้วข้ามแถว
4. **สมบูรณ์ / ต้องตรวจ**: ดู `visibility` ของข้อต่อที่ท่านั้นใช้ (`REQUIRED_POINTS[exercise]`) ที่ข้างที่บันทึก (`row["side"]`) คอลัมน์คือ `v<เลขดัชนี>` โดยเลขดัชนี = `LANDMARK_INDEX[side][ชื่อข้อต่อ]` ถ้าค่าต่ำสุด ≥ `VISIBILITY_MIN` → `complete` + 1 ไม่งั้น `check` + 1 (ทั้งสองแบบยังเก็บไว้ใช้)
5. เพิ่มมุม 3 ค่า (อ่านตามชื่อใน `EXERCISES[exercise]["angles"]` เก็บใน `angle_names`) เข้า `groups[exercise][label]`

### `count_discarded(exercise)`

อ่าน `CLEAN_LOG` (ถ้าไม่มีไฟล์คืน `{}`) นับแถวที่ `exercise` ตรงกันและ `status != "ok"` แยกตามสถานะ คืน `status_counts` = `{สถานะ: จำนวน}`

### `percent(part, whole)`

`100 × part / whole` ถ้า `whole` เป็น 0 คืน `0.0`

### `build_templates(paths)`

1. `groups, clean_counts = load_dataset(paths)`
2. ถ้ามี `templates.json` อยู่แล้ว อ่านมาก่อนเก็บใน `templates` (ท่าที่ไม่ได้อยู่ใน CSV รอบนี้จะได้ไม่หาย)
3. แต่ละท่า พิมพ์ 2 ส่วน แล้วเก็บค่าเฉลี่ยเป็นท่าต้นแบบ
4. เขียน `templates.json` ด้วย `json.dump(..., indent=2, ensure_ascii=False)`

**ส่วน clean** (ใช้ตอบข้อกำหนดรายงาน: สัดส่วนข้อมูลสมบูรณ์ / แก้ไขได้ / ตัดทิ้ง, ก่อน-หลัง)

```
discarded_count = จำนวนภาพที่ใช้ไม่ได้ จาก count_discarded
count_before    = rows + discarded_count            ข้อมูลทั้งหมดที่ป้อนเข้า
dropped_count   = discarded_count + duplicate       ที่ตัดทิ้ง
หลัง clean      = count_before − dropped_count

สมบูรณ์ %        = complete / count_before
ต้องตรวจ/แก้ไข %  = check / count_before
ตัดทิ้ง %         = dropped_count / count_before    (บอกด้วยว่าเป็นแถวซ้ำกี่แถว และแต่ละสาเหตุกี่ภาพ จาก SKIP_REASON)
```

**ส่วนสถิติแต่ละ label** `angle_matrix` = เมทริกซ์ n×3 ของ label นั้น

| ค่า | วิธีหา |
|---|---|
| n และ % ของท่านั้น | `len(angle_matrix)`, `percent(len(angle_matrix), รวมทุก label)` |
| ค่าเฉลี่ย (= ท่าต้นแบบ) | `angle_matrix.mean(axis=0)` |
| ส่วนเบี่ยงเบนมาตรฐาน | `angle_matrix.std(axis=0)` |
| ต่ำสุด / สูงสุด | `angle_matrix.min(axis=0)`, `angle_matrix.max(axis=0)` |

ท่าต้นแบบของ label = **เวกเตอร์ค่าเฉลี่ย** ของมุมทุกแถว บันทึกเป็น `angle_matrix.mean(axis=0).round(2).tolist()`

### `evaluate(paths, test_ratio=0.2, seed=0)`

ไม่เขียนทับ `templates.json`

1. `groups, _ = load_dataset(paths)`; `random_generator = np.random.default_rng(seed)`
2. แต่ละท่า แต่ละ label ที่มีเมทริกซ์ `angle_matrix` (n แถว)
   - จำนวนข้อมูลทดสอบ `test_count = max(1, round(n × test_ratio))` ถ้า n ≥ 2 ไม่งั้น `0`
   - สุ่มลำดับ `shuffled_indices = random_generator.permutation(n)` → `test_count` ตัวแรกเป็นข้อมูลทดสอบ (`test_samples`), ที่เหลือเป็น train
   - ท่าต้นแบบของ label = ค่าเฉลี่ยของ train
3. ถ้าไม่มีข้อมูลทดสอบเลย พิมพ์ว่าข้อมูลน้อยเกินไป แล้วข้ามท่านั้น
4. สร้าง confusion matrix (`confusion`) ขนาด (จำนวน label) × (จำนวน label) ชนิด int เริ่มจาก 0 ทุกช่อง
5. ทุกตัวอย่างทดสอบ: `predicted_label` = label ที่ `euclidean(angle_values, ท่าต้นแบบ)` น้อยที่สุด → ช่อง `[แถว = label จริง, คอลัมน์ = predicted_label]` + 1
6. `accuracy = trace(confusion) / ผลรวมทุกช่อง` (ผลรวมแนวทแยง = จำนวนที่ทายถูก)
7. พิมพ์จำนวน train/test, ตาราง confusion matrix พร้อมชื่อ label ที่หัวแถวและหัวคอลัมน์, accuracy

แบ่งแยกตาม label (stratified) เพื่อให้ทุก label มีทั้งใน train และ test

ทดสอบ: หลังงาน D merge แล้ว เก็บข้อมูลทดลองไม่กี่ภาพ แล้วรัน

```bash
python pose_coach.py --build-templates data_squat.csv
```

```bash
python pose_coach.py --evaluate data_squat.csv
```

`--test-ratio 0` = ไม่แบ่งข้อมูล ใช้ท่าต้นแบบจริงใน `templates.json` ทายทุกแถว (ค่าที่ใช้ในรายงาน: 312/360 = 86.7%)

```bash
python pose_coach.py --evaluate data_squat.csv data_pushup.csv data_lunge.csv --test-ratio 0
```

ตรวจว่า n รวมตรงกับจำนวนภาพที่ใช้ได้ และ complete + check + ตัดทิ้ง = count_before หลังทดลองเสร็จลบ `templates.json` และ CSV ทดลองทิ้ง

## เสร็จเมื่อ

- [ ] `python selftest.py` ผ่านทั้งหมด (8 ต.ค.)
- [ ] `--build-templates` พิมพ์สถิติครบและเขียน `templates.json` (11 ต.ค.)
- [ ] `--evaluate` พิมพ์ confusion matrix และ accuracy (11 ต.ค.)
- [ ] เปิด pull request และ merge เข้า `main` (แยก 2 รอบตามไฟล์)

## คำถามที่อาจารย์อาจถาม (เตรียมตอบ)

- ท่าต้นแบบมาจากไหน ทำไมใช้ค่าเฉลี่ย
- ทำไมต้องแบ่ง train/test ไม่วัดกับข้อมูลชุดเดียวกัน
- อ่าน confusion matrix ยังไง ท่าไหนสับสนกับท่าไหน
- ทำไมใช้ M⁻¹ (`inverse_matrix`) ตอนวาดเส้นท่าที่ถูก
