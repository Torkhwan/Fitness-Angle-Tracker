# งาน D: รับภาพและแสดงผล

ไฟล์: `posecoach/capture.py`, `posecoach/pose_coach.py` | ส่งภายใน **9 ต.ค. 69**

อ่าน [shared_structure.md](shared_structure.md) ข้อ 1, 3, 8, 9, 10, 12 ก่อน

## งานนี้ทำอะไร

เป็นส่วนที่ติดต่อกับโลกภายนอก: เปิดภาพหรือกล้อง ให้ MediaPipe หาพิกัดข้อต่อ ส่งให้ `analyze` (งาน C) แล้วบันทึกข้อมูลลง CSV และวาดผลลงภาพ งานนี้ไม่มีสูตรคำนวณ แต่ไฟล์ CSV ที่งานนี้เขียนคือข้อมูลทั้งหมดของโครงงาน คอลัมน์จึงต้องตรงตามที่ตกลงไว้ทุกตัว

เขียนโค้ดได้ตั้งแต่วันแรก แต่จะรันทดสอบกับภาพได้เมื่องาน C (`analyze.py`) merge เข้า `main` แล้ว (8 ต.ค.)

`import cv2` และ `import mediapipe` ให้เขียน **ในฟังก์ชันที่ใช้** ไม่เขียนที่หัวไฟล์ เพื่อให้ `selftest` รันได้เร็วและรันได้แม้เครื่องยังไม่ได้ลงสองตัวนี้

ชื่อตัวแปรใช้คำเต็มตามข้อตกลง (shared_structure ข้อ 12) ชื่อที่ใช้บ่อยในงานนี้: `exercise`, `image`, `points`, `landmarks`, `detection`, `result`, `angle_values`

## `capture.py`

### `make_landmarker(video=False)`

```python
import mediapipe
from mediapipe.tasks import python as mediapipe_python
from mediapipe.tasks.python import vision
```

1. ถ้ายังไม่มีไฟล์ `MODEL_PATH` → พิมพ์บอกว่ากำลังดาวน์โหลด แล้ว `urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)`
2. สร้าง `options = vision.PoseLandmarkerOptions(...)` โดย
   - `base_options=mediapipe_python.BaseOptions(model_asset_path=MODEL_PATH)`
   - `running_mode` = `vision.RunningMode.VIDEO` ถ้า `video` ไม่งั้น `vision.RunningMode.IMAGE`
   - `num_poses=1`
3. คืน `(mediapipe, vision.PoseLandmarker.create_from_options(options))`

### `extract(exercise, detection, width, height)`

`detection` = ผลตรวจจับจาก MediaPipe, `width` `height` = ขนาดภาพ คืน 4 ค่าเสมอ: `(side, points, landmarks, status)`

ใช้ชื่อ `detection` กับผลของ MediaPipe เพื่อไม่ให้สับสนกับ `result` ซึ่งหมายถึงผลการวิเคราะห์ท่าจาก `analyze`

1. ถ้า `detection.pose_landmarks` ว่าง → คืน `(None, None, None, "no_person")`
2. `landmarks = detection.pose_landmarks[0]` (list 33 จุด แต่ละจุดมี `.x` `.y` ค่า 0-1 และ `.visibility`)
3. พิกัด pixel ของจุดลำดับที่ `index` = `np.array([landmarks[index].x * width, landmarks[index].y * height])`
4. **เลือกข้าง**: แต่ละข้าง (`"left"`, `"right"`) หาค่าเฉลี่ย visibility ของข้อต่อใน `REQUIRED_POINTS[exercise]` (เลขดัชนีจาก `LANDMARK_INDEX[ข้าง][ชื่อข้อต่อ]`) เลือกข้างที่ค่าเฉลี่ยสูงกว่าเป็น `side`
5. ถ้าค่าเฉลี่ยของข้างที่เลือก < `VISIBILITY_MIN` → คืน `(None, None, None, "low_visibility")`
6. สร้าง `points`
   - `squat`, `pushup`: `{ชื่อข้อต่อ: พิกัด}` ของข้อต่อใน `REQUIRED_POINTS[exercise]` จากข้างที่เลือก
   - `lunge`: `shoulder_point`, `hip_point` จากข้างที่เลือก และ `knee_point` `ankle_point` `heel_point` `toe_point` ของ **ทั้งสองข้าง** ตั้งชื่อโดยเติมชื่อข้างไว้หน้า เช่น `left_knee_point`, `right_knee_point` (ประกอบด้วย `f"{side_name}_{point_name}"`)
7. คืน `(side, prepare_points(exercise, points), landmarks, "ok")`

### `save_row(path, exercise, label, side, angle_values, landmarks)`

ต่อท้าย 1 แถว (เปิดไฟล์ด้วย `"a"`, `newline=""`, `encoding="utf-8"`) ถ้าไฟล์ยังไม่มีให้เขียนหัวตารางก่อน คอลัมน์และจำนวนทศนิยมตาม shared_structure ข้อ 10

- เวลา: `time.strftime("%Y-%m-%d %H:%M:%S")`
- ชื่อมุม (`angle_names`): ตัวแรกของแต่ละรายการใน `EXERCISES[exercise]["angles"]`
- พิกัด 66 ค่า เรียง `x0, y0, x1, y1, …` ใช้ค่า `.x` `.y` จาก MediaPipe ตรง ๆ (ไม่คูณขนาดภาพ)
- เสร็จแล้วพิมพ์บอกว่าบันทึกลงไฟล์ไหน

รวม 4 + 3 + 66 + 33 = 106 คอลัมน์ งาน C อ่านไฟล์นี้ด้วยชื่อคอลัมน์ ถ้าชื่อผิดงาน C จะพัง

### `log_clean(exercise, label, path, status)`

ต่อท้าย 1 แถวใน `CLEAN_LOG`: `time, exercise, label, image, status` โดย `image` = ชื่อไฟล์อย่างเดียว (`os.path.basename`) เขียนหัวตารางถ้าเป็นไฟล์ใหม่

### `draw(image, points, result)`

วาดลง `image` แล้วคืน `image` สีของ OpenCV เรียง (น้ำเงิน, เขียว, แดง)

| วาด | รายละเอียด |
|---|---|
| สีหลัก (`color`) | `result["ranking"][0]["name"] == "correct"` → เขียว `(0, 200, 0)` ไม่งั้นแดง `(0, 0, 255)` |
| โครงร่าง | ทุกคู่ชื่อข้อต่อใน `EXERCISES[exercise]["lines"]` → `cv2.line` ระหว่างสองจุดนั้น สีหลัก หนา 4 |
| ข้อต่อ | ทุกจุดใน `points` → `cv2.circle` สีขาว รัศมี 6 ทึบ |
| ท่าที่ถูก | ทุกเส้นใน `result["ghosts"]` → เส้นสีเหลือง `(0, 255, 255)` หนา 3 และวงกลมที่ปลายเส้น |
| ข้อความ | 3 บรรทัดมุมบนซ้าย: ค่ามุมจาก `result["angle_values"]`, `ท่า: label (distance=ระยะ Euclidean)`, `yellow = correct form` |

พิกัดที่ส่งให้ OpenCV ต้องเป็น tuple ของ int ข้อความใช้ภาษาอังกฤษเพราะ `cv2.putText` แสดงภาษาไทยไม่ได้ เขียนข้อความสองรอบ (สีดำหนา แล้วทับด้วยสีหลักบาง) จะอ่านง่ายบนทุกพื้นหลัง

### `run_image(exercise, path, explain, label, save, landmarker_pair=None, output_folder=None)`

คืนสถานะ (shared_structure ข้อ 9)

1. `mediapipe, landmarker = landmarker_pair or make_landmarker(video=False)`
2. `image = cv2.imread(path)` ถ้าได้ None → สถานะ `"unreadable"`
3. ไม่งั้น: แปลงสี BGR → RGB, สร้าง `mediapipe.Image(image_format=mediapipe.ImageFormat.SRGB, data=...)`, เรียก `landmarker.detect(...)` ได้ `detection`, แล้ว `extract`
4. ถ้าสถานะ `"ok"` → `result = analyze(exercise, points, explain=explain)` ครอบด้วย `try` ถ้าเกิด `ValueError` หรือ `ZeroDivisionError` → สถานะ `"calc_error"`
5. **ถ้ามี `label` → `log_clean` ทุกครั้ง** ไม่ว่าสถานะอะไร (ใช้นับภาพที่ตัดทิ้งในรายงาน)
6. สถานะไม่ใช่ `"ok"` → พิมพ์ `ข้าม <ชื่อไฟล์>: <SKIP_REASON[สถานะ]>` แล้วคืนสถานะ
7. สถานะ `"ok"` → พิมพ์ข้างที่ใช้, `print_result(result)`, ถ้ามี `label` → `save_row(save or f"data_{exercise}.csv", ...)`
8. บันทึกรูปผลลัพธ์ชื่อ `<ชื่อเดิม>_result.jpg` ลง `output_folder` (สร้างโฟลเดอร์ถ้ายังไม่มี) หรือโฟลเดอร์เดียวกับภาพถ้าไม่ได้ระบุ

### `run_folder(exercise, folder, explain, label, save)`

1. รายชื่อไฟล์ในโฟลเดอร์ที่นามสกุลอยู่ใน `IMAGE_EXTENSIONS` (เทียบแบบตัวเล็ก) เรียงตามชื่อ ไม่มีไฟล์ → `sys.exit` พร้อมข้อความ
2. สร้าง landmarker **ครั้งเดียว** เก็บใน `landmarker_pair` แล้วส่งให้ `run_image` ทุกภาพ (สร้างใหม่ทุกภาพจะช้ามาก)
3. `output_folder` = `<folder>/results`
4. นับจำนวนแต่ละสถานะ (`status_counts`) แล้วพิมพ์สรุป: ทั้งหมดกี่ภาพ ใช้ได้กี่ภาพ ใช้ไม่ได้เพราะอะไรกี่ภาพ

### `run_camera(exercise, camera_index, save)`

1. `make_landmarker(video=True)`, `camera = cv2.VideoCapture(camera_index)` เปิดไม่ได้ → `sys.exit("เปิดกล้องไม่ได้")`
2. ปุ่ม `1` `2` `3` = label ตามลำดับใน `EXERCISES[exercise]["templates"]` (เก็บเป็น `key_to_label`) พิมพ์วิธีใช้ปุ่มก่อนเริ่ม (ทำใน `camera_mode(exercise)` ซึ่งคืนชื่อหน้าต่างและ `key_to_label`)
   - หน้าต่าง `cv2.namedWindow("FAT Pose Coach", cv2.WINDOW_NORMAL)` ขนาดเริ่มต้น 1280×960 ลากขยายได้ ชื่อบนแถบเป็น `FAT Pose Coach - <ท่า>` (`cv2.setWindowTitle`)
   - `set_window_icon(ชื่อหน้าต่าง)` ใส่ไอคอน `fat.ico` ที่หน้าต่างและ taskbar (Windows เท่านั้น ระบบอื่นข้ามไป)
3. วนอ่านเฟรม
   - ตรวจด้วย `landmarker.detect_for_video(ภาพ, เวลาเป็นมิลลิวินาทีนับจาก start_time)` (เวลาต้องเพิ่มขึ้นทุกเฟรม)
   - `extract` ได้จุด → `analyze` → เก็บ `side`, `points`, `landmarks`, `result` ของเฟรมล่าสุดไว้ใน `last_frame`
   - ถ้า `EXERCISES[exercise]["gate"](result["angle_values"])` เป็นจริง (อยู่ในช่วงลงท่า) → `draw` ไม่งั้นเขียนข้อความบอกให้ลงท่า
   - ไม่พบจุด → เขียนข้อความบอกให้หันข้างให้เห็นทั้งตัว
   - ดัก `ValueError`, `ZeroDivisionError` จาก `analyze` แล้วข้ามเฟรมนั้น
   - `cv2.imshow`, `pressed_key = cv2.waitKey(1) & 0xFF`
   - `q` ออก / `1` `2` `3` → `save_row` ด้วยเฟรมล่าสุด / `e` → `analyze(..., explain=True)` กับเฟรมล่าสุด
   - `s` `p` `l` → สลับเป็น squat / pushup / lunge ทันที (เรียก `camera_mode` ใหม่ เปลี่ยนชื่อหน้าต่างและปุ่ม 1 2 3) `--save` ใช้กับท่าเริ่มต้นเท่านั้น ท่าอื่นบันทึกลง `data_<ท่า>.csv`
4. จบแล้ว `camera.release()` และ `cv2.destroyAllWindows()`

## `pose_coach.py`: `main()`

ใช้ `argparse` (ตัวแปร `parser` และ `arguments`)

| argument | รูปแบบ |
|---|---|
| `--exercise` | `choices=list(EXERCISES)`, ค่าเริ่มต้น `"squat"` |
| `--selftest` | `action="store_true"` |
| `--image` | ไฟล์ภาพ หรือโฟลเดอร์ภาพ |
| `--camera` | `type=int` |
| `--explain` | `action="store_true"` |
| `--label` | ข้อความ |
| `--save` | ไฟล์ CSV (ไม่ใส่ = `data_<exercise>.csv`) |
| `--build-templates` | `metavar="CSV"`, `nargs="+"` |
| `--evaluate` | `metavar="CSV"`, `nargs="+"` |
| `--test-ratio` | `type=float`, ค่าเริ่มต้น `0.2` (`0` = ใช้ templates.json ทายทุกแถว) |

ลำดับการตรวจ (เจออันไหนก่อนทำอันนั้นแล้วจบ)

1. มี `--label` แต่ไม่ใช่ label ของท่านั้น → `sys.exit` บอก label ที่ใช้ได้
2. `--selftest` → `sys.exit(0 if selftest() else 1)`
3. `--build-templates` → `build_templates(...)`
4. `--evaluate` → `evaluate(..., test_ratio)`
5. `--image` เป็นโฟลเดอร์ (`os.path.isdir`) → `run_folder(...)`
6. `--image` เป็นไฟล์ → `run_image(...)` แล้ว `sys.exit(0)` ถ้าได้ `"ok"` ไม่งั้น `sys.exit(1)`
7. `--camera` ถูกระบุ (เทียบ `is not None` เพราะกล้องตัวแรกคือเลข 0) → `run_camera(...)`
8. ไม่ใส่อะไรเลย → `parser.print_help()`

## ทดสอบ

ใช้รูปตัวเองถ่ายด้านข้าง 3-4 รูป ใส่โฟลเดอร์ `photos/test/` (โฟลเดอร์ `photos/` ไม่ถูก push)

```bash
python pose_coach.py --selftest
```

```bash
python pose_coach.py --exercise squat --image photos/test --label correct --save test.csv
```

```bash
python pose_coach.py --exercise squat --camera 0
```

ตรวจว่า

- มีรูปใน `photos/test/results/` เส้นทับตัวคนถูกตำแหน่ง เส้นเหลืองออกจากสะโพก
- `test.csv` มีหัวตาราง 106 คอลัมน์ และจำนวนแถว = จำนวนภาพที่ใช้ได้
- `clean_log.csv` มีแถวครบทุกภาพที่ป้อน รวมภาพที่ใช้ไม่ได้ (ลองใส่ภาพที่ไม่มีคน 1 ภาพ)
- กล้อง: ปุ่ม `1` `2` `3` `e` `q` `s` `p` `l` ทำงาน หน้าต่างลากขยายได้ และมีไอคอน FAT

ทดสอบเสร็จลบ `test.csv` และ `clean_log.csv` ทิ้ง ไม่ commit ไฟล์ทดลอง

## เสร็จเมื่อ

- [ ] ตรวจภาพเดียว ทั้งโฟลเดอร์ และกล้องได้
- [ ] CSV และ clean_log ถูกรูปแบบ
- [ ] ทุกคำสั่งในหัวไฟล์ `pose_coach.py` รันได้
- [ ] เปิด pull request และ merge เข้า `main`

## คำถามที่อาจารย์อาจถาม (เตรียมตอบ)

- MediaPipe ทำส่วนไหน เราเขียนเองส่วนไหน
- เวกเตอร์ข้อมูล 1 ชุดมีกี่มิติ เก็บอะไรบ้าง
- ภาพแบบไหนถูกตัดทิ้ง ตัดสินจากอะไร
- เส้นเหลืองบนภาพมาจากไหน
