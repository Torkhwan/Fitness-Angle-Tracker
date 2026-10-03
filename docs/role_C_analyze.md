# งาน C: วิเคราะห์ผล

ไฟล์: `posecoach/analyze.py` ส่งภายใน **8 ต.ค. 69** | `posecoach/dataset.py` ส่งภายใน **11 ต.ค. 69**

อ่าน [shared_structure.md](shared_structure.md) ทั้งหน้า โดยเฉพาะข้อ 6, 8, 10

## งานนี้ทำอะไร

- `analyze.py` ต่อฟังก์ชันของงาน A และ B เข้าด้วยกันเป็นสายเดียว: พิกัดภาพ → normalize → features → เทียบท่าต้นแบบ → คำแนะนำ
- `dataset.py` อ่านข้อมูลที่เก็บมา clean ทำสถิติสำหรับรายงาน สร้างท่าต้นแบบจากค่าเฉลี่ย และวัดความแม่นยำ

## ส่วนที่ 1: `analyze.py`

### `load_templates(ex)`

คืน `(templates, from_file)` โดย `templates` = `{label: np.array 3 ค่า (float)}`

1. ถ้ามีไฟล์ `TEMPLATE_PATH` → เปิดด้วย `encoding="utf-8"` อ่านด้วย `json.load` ถ้ามี key `ex` → คืนค่าจากไฟล์กับ `True`
2. ไม่งั้นคืนค่าสมมติจาก `EXERCISES[ex]["templates"]` กับ `False`

### `analyze(ex, pts_img, explain=False, templates=None)`

| ขั้น | ทำอะไร | ใช้ |
|---|---|---|
| 1 | `Fy = reflect_y()`; `P` = ทุกจุดใน `pts_img` ผ่าน `apply(Fy, จุด)` | งาน A |
| 2 | `M, info = normalization_matrix(ex, P)` | งาน A |
| 3 | `Q` = ทุกจุดใน `P` ผ่าน `apply(M, จุด)` | งาน A |
| 4 | `x, extra = compute_features(ex, Q)` | งาน B |
| 5 | ถ้า `templates` เป็น None → `load_templates(ex)` (ไม่งั้น `from_file = False`) | |
| 6 | `ranking`: ทุก label คำนวณระยะจาก `x` ถึงท่าต้นแบบ แล้วเรียงตาม Euclidean น้อย → มาก | งาน B |
| 7 | `ref` = ท่าต้นแบบ `correct` (ถ้าไม่มี ใช้ตัวแรก); `diff = x − ref` | |
| 8 | `checks` และ `tips` (ดูด้านล่าง) | |
| 9 | `M_inv = gauss_jordan_inverse(M)` | งาน A |
| 10 | `ghosts`: ทุกเส้นจาก `ghost_segments(ex, Q, ref)` แปลงปลายทั้งสองกลับพิกัดภาพ | งาน A, B |
| 11 | รวมทุกอย่างเป็น dict `r` (key ครบตาม shared_structure ข้อ 8) | |
| 12 | ถ้า `explain` → `print_explain(pts_img, r)` แล้วคืน `r` | งาน A |

**ขั้น 6: nearest template**

```
แต่ละ label n ที่มีท่าต้นแบบ t:   {"name": n, "euclid": euclidean(x, t), "manhattan": manhattan(x, t), "cosine": cosine(x, t)}
label ที่ระบบทาย = ตัวที่ euclid น้อยที่สุด = ranking[0]
```

ตัดสินด้วย Euclidean เท่านั้น Manhattan กับ Cosine เก็บไว้พิมพ์เทียบในรายงาน

**ขั้น 8: checks และ tips** วนทุก feature ลำดับที่ `i` (`ชื่อไทย`, `hi`, `lo` มาจาก `EXERCISES[ex]["features"][i]`)

- `checks` เพิ่ม `(ชื่อไทย, diff[i], abs(diff[i]) <= TOLERANCE)`
- ถ้า `diff[i] > TOLERANCE` และ `hi` ไม่ว่าง → `tips` เพิ่ม `hi.format(d=diff[i])`
- ถ้า `diff[i] < −TOLERANCE` และ `lo` ไม่ว่าง → `tips` เพิ่ม `lo.format(d=−diff[i])`

**ขั้น 10: แปลงกลับ** จุด `p` ในพิกัดมาตรฐาน → พิกัดภาพ = `apply(Fy, apply(M_inv, p))`

M⁻¹ ย้อนการ normalize (Q → P) แล้ว Fy กลับแกน y อีกครั้ง (P → ภาพ) เพราะ Fy เป็น inverse ของตัวเอง แต่ละเส้นเก็บเป็น tuple `(จุดเริ่ม, จุดปลาย)`

**ตัวอย่างตรวจมือ** (ท่าต้นแบบค่าสมมติของ squat)

```
x = [63.43, 36.87, 53.13]
lean_forward = [65, 35, 55]   diff = (−1.57, 1.87, −1.87)   Euclid = √(2.46 + 3.50 + 3.50) = 3.07   ← ใกล้ที่สุด
correct      = [65, 55, 35]   diff = (−1.57, −18.13, 18.13)  → มุมโน้มตัวเกิน 18° > TOLERANCE → มีคำแนะนำ
```

### `print_result(r)`

พิมพ์ตามลำดับ

1. `[ชื่อท่าไทย] features = ...` ทศนิยม 1 ตำแหน่ง
2. `ผล: ใกล้เคียง "<ข้อความไทยของ label ที่ทาย>" มากที่สุด` (ข้อความจาก `EXERCISES[ex]["labels"]`)
3. แต่ละรายการใน `r["checks"]`: ชื่อไทย, ต่างจากท่าถูกกี่องศา (มีเครื่องหมาย + −), ผ่าน/ไม่ผ่าน
4. แต่ละรายการใน `r["tips"]`: `คำแนะนำ: ...`
5. ถ้า `r["from_file"]` เป็น False: เตือนว่ายังใช้ท่าต้นแบบค่าสมมติ ให้เก็บข้อมูลแล้วรัน `--build-templates`

ทดสอบ (ต้องมีงาน A และ B ใน `main` แล้ว กด Update from main ก่อน)

```bash
python selftest.py
```

ต้องขึ้น `SELFTEST: ผ่านทั้งหมด ✔`

## ส่วนที่ 2: `dataset.py`

รูปแบบไฟล์ CSV ดู shared_structure ข้อ 10 เปิดไฟล์ทุกครั้งใส่ `encoding="utf-8"`

### `load_dataset(paths)`

คืน `(groups, clean)`

- `groups` = `{ท่า: {label: np.array ขนาด n×3}}` 1 แถว = features ของ 1 ภาพ
- `clean` = `{ท่า: {"rows": .., "duplicate": .., "complete": .., "check": ..}}`

วนทุกไฟล์ อ่านด้วย `csv.DictReader` ทุกแถว

1. ถ้าไฟล์ไม่มีคอลัมน์ `exercise` → `sys.exit` พร้อมข้อความบอกว่าเป็นรูปแบบเก่า
2. `rows` + 1
3. **แถวซ้ำ**: สร้าง key เป็น tuple ของพิกัด 66 ค่า (`x0, y0, …, x32, y32`) ถ้าเคยเจอแล้ว (เก็บใน `set`) → `duplicate` + 1 แล้วข้ามแถว
4. **สมบูรณ์ / ต้องตรวจ**: ดู visibility ของข้อต่อที่ท่านั้นใช้ (`NEED[ex]`) ที่ข้างที่บันทึก (`row["side"]`) คอลัมน์คือ `v<เลขดัชนี>` โดยเลขดัชนี = `LM[side][ชื่อข้อต่อ]` ถ้าค่าต่ำสุด ≥ `VIS_MIN` → `complete` + 1 ไม่งั้น `check` + 1 (ทั้งสองแบบยังเก็บไว้ใช้)
5. เพิ่ม features 3 ค่า (อ่านตามชื่อใน `EXERCISES[ex]["features"]`) เข้า `groups[ex][label]`

### `count_discarded(ex)`

อ่าน `CLEAN_LOG` (ถ้าไม่มีไฟล์คืน `{}`) นับแถวที่ `exercise == ex` และ `status != "ok"` แยกตามสถานะ คืน `{สถานะ: จำนวน}`

### `pct(a, b)`

`100 × a / b` ถ้า `b` เป็น 0 คืน `0.0`

### `build_templates(paths)`

1. `groups, clean = load_dataset(paths)`
2. ถ้ามี `templates.json` อยู่แล้ว อ่านมาก่อน (ท่าที่ไม่ได้อยู่ใน CSV รอบนี้จะได้ไม่หาย)
3. แต่ละท่า พิมพ์ 2 ส่วน แล้วเก็บค่าเฉลี่ยเป็นท่าต้นแบบ
4. เขียน `templates.json` ด้วย `json.dump(..., indent=2, ensure_ascii=False)`

**ส่วน clean** (ใช้ตอบข้อกำหนดรายงาน: สัดส่วนข้อมูลสมบูรณ์ / แก้ไขได้ / ตัดทิ้ง, ก่อน-หลัง)

```
n_disc = จำนวนภาพที่ใช้ไม่ได้ จาก count_discarded
before = rows + n_disc                  ข้อมูลทั้งหมดที่ป้อนเข้า
drop   = n_disc + duplicate             ที่ตัดทิ้ง
after  = before − drop

สมบูรณ์ %       = complete / before
ต้องตรวจ/แก้ไข % = check / before
ตัดทิ้ง %        = drop / before         (บอกด้วยว่าเป็นแถวซ้ำกี่แถว และแต่ละสาเหตุกี่ภาพ จาก SKIP_REASON)
```

**ส่วนสถิติแต่ละ label** `A` = เมทริกซ์ n×3 ของ label นั้น

| ค่า | วิธีหา |
|---|---|
| n และ % ของท่านั้น | `len(A)`, `pct(len(A), รวมทุก label)` |
| ค่าเฉลี่ย (= ท่าต้นแบบ) | `A.mean(axis=0)` |
| ส่วนเบี่ยงเบนมาตรฐาน | `A.std(axis=0)` |
| ต่ำสุด / สูงสุด | `A.min(axis=0)`, `A.max(axis=0)` |

ท่าต้นแบบของ label = **เวกเตอร์ค่าเฉลี่ย** ของ features ทุกแถว บันทึกเป็น `A.mean(axis=0).round(2).tolist()`

### `evaluate(paths, test_ratio=0.2, seed=0)`

ไม่เขียนทับ `templates.json`

1. `groups, _ = load_dataset(paths)`; `rng = np.random.default_rng(seed)`
2. แต่ละท่า แต่ละ label ที่มีเมทริกซ์ `A` (n แถว)
   - จำนวนข้อมูลทดสอบ `k = max(1, round(n × test_ratio))` ถ้า n ≥ 2 ไม่งั้น `k = 0`
   - สุ่มลำดับ `idx = rng.permutation(n)` → `k` ตัวแรกเป็น test, ที่เหลือเป็น train
   - ท่าต้นแบบของ label = ค่าเฉลี่ยของ train
3. ถ้าไม่มี test เลย พิมพ์ว่าข้อมูลน้อยเกินไป แล้วข้ามท่านั้น
4. สร้าง confusion matrix ขนาด (จำนวน label) × (จำนวน label) ชนิด int เริ่มจาก 0 ทุกช่อง
5. ทุกตัวอย่าง test: ทาย = label ที่ `euclidean(x, ท่าต้นแบบ)` น้อยที่สุด → ช่อง `[แถว = label จริง, คอลัมน์ = label ที่ทาย]` + 1
6. `accuracy = trace(conf) / ผลรวมทุกช่อง` (ผลรวมแนวทแยง = จำนวนที่ทายถูก)
7. พิมพ์จำนวน train/test, ตาราง confusion matrix พร้อมชื่อ label ที่หัวแถวและหัวคอลัมน์, accuracy

แบ่งแยกตาม label (stratified) เพื่อให้ทุก label มีทั้งใน train และ test

ทดสอบ: หลังงาน D merge แล้ว เก็บข้อมูลทดลองไม่กี่ภาพ แล้วรัน

```bash
python pose_coach.py --build-templates data_squat.csv
```

```bash
python pose_coach.py --evaluate data_squat.csv
```

ตรวจว่า n รวมตรงกับจำนวนภาพที่ใช้ได้ และ complete + check + ตัดทิ้ง = before หลังทดลองเสร็จลบ `templates.json` และ CSV ทดลองทิ้ง

## เสร็จเมื่อ

- [ ] `python selftest.py` ผ่านทั้งหมด (8 ต.ค.)
- [ ] `--build-templates` พิมพ์สถิติครบและเขียน `templates.json` (11 ต.ค.)
- [ ] `--evaluate` พิมพ์ confusion matrix และ accuracy (11 ต.ค.)
- [ ] เปิด pull request และ merge เข้า `main` (แยก 2 รอบตามไฟล์)

## คำถามที่อาจารย์อาจถาม (เตรียมตอบ)

- ท่าต้นแบบมาจากไหน ทำไมใช้ค่าเฉลี่ย
- ทำไมต้องแบ่ง train/test ไม่วัดกับข้อมูลชุดเดียวกัน
- อ่าน confusion matrix ยังไง ท่าไหนสับสนกับท่าไหน
- ทำไมใช้ M⁻¹ ตอนวาดเส้นท่าที่ถูก
