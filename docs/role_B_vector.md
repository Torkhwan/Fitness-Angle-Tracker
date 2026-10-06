# งาน B: เวกเตอร์

ไฟล์: `posecoach/vector.py`, `posecoach/angles.py` | ส่งภายใน **6 ต.ค. 69** | ทฤษฎี: บท 1, 2

อ่าน [shared_structure.md](shared_structure.md) ข้อ 1-4 ก่อน

งานนี้ส่งเป็นงานแรก เพราะทุกไฟล์เรียกใช้ `vector.py` ถ้าทำ `vector.py` เสร็จก่อน ให้เปิด pull request ส่วนนั้นก่อนได้เลย

## งานนี้ทำอะไร

แปลงจุดข้อต่อ (ที่ normalize แล้ว) ให้เป็นมุม 3 ค่าต่อท่า ด้วย dot product, projection และ cross product และเตรียมฟังก์ชันวัดระยะทางให้งาน C ใช้เทียบท่าต้นแบบ

ห้ามใช้ `np.linalg.norm` (ใช้ `@` หา dot product ได้)

## ส่วนที่ 1: `vector.py`

| ฟังก์ชัน | สูตร | คืน |
|---|---|---|
| `norm(v)` | \|v\| = √(v · v) | float |
| `angle_between(u, v)` | cos φ = (u · v) / (\|u\| \|v\|) → φ = arccos | องศา 0-180 |
| `angle_at(center, p1, p2)` | มุมระหว่าง `p1 − center` กับ `p2 − center` | องศา |
| `projection(t, b)` | comp = (t · b) / \|b\|, proj = ((t · b) / (b · b)) b, perp = t − proj | `(comp, proj, perp)` |
| `cross_z(u, v)` | u₀v₁ − u₁v₀ | float |
| `euclidean(a, b)` | \|a − b\| | float |
| `manhattan(a, b)` | Σ \|aᵢ − bᵢ\| | float |
| `cosine(a, b)` | (a · b) / (\|a\| \|b\|) | float |
| `signed_from_vertical(v)` | ดูด้านล่าง | องศา −180 ถึง 180 |

ข้อควรระวัง

- **`angle_between`**: ค่า cos ที่คำนวณได้อาจเกินช่วงเล็กน้อยจากการปัดเศษ เช่น 1.0000000002 ทำให้ `math.acos` error ต้องบีบให้อยู่ใน [−1, 1] ก่อน: `max(-1.0, min(1.0, c))`
- **`angle_at`**: เวกเตอร์สองตัวต้องเริ่มจากข้อต่อ `center` ทั้งคู่ ถ้าลบกลับด้านจะได้มุมผิด
- ค่าที่คืนเป็นตัวเลขเดี่ยวให้ครอบด้วย `float(...)` จะได้ไม่ติดชนิด `np.float64` ตอนพิมพ์

**`signed_from_vertical(v)`** มุมที่ v เอียงจากแนวตั้ง มีเครื่องหมาย

1. `comp, _, perp = projection(v, J)` (J = (0, 1) ประกาศไว้ต้นไฟล์แล้ว)
2. `ang = arccos(comp / |v|)` เป็นองศา (บีบค่าให้อยู่ใน [−1, 1] ก่อนเหมือนกัน)
3. ถ้า `perp[0] >= 0` (เอียงไปทาง +x = ข้างหน้า) คืน `ang` ไม่งั้นคืน `−ang`

comp คือความยาวของ v ในแนวตั้ง, perp คือส่วนที่เหลือในแนวนอน เครื่องหมายของ perp บอกว่าเอียงไปทางไหน

ทดสอบ

```bash
python check.py vector
```

## ส่วนที่ 2: `angles.py`

### `prepare_points(ex, pts)`

ท่าที่ไม่ใช่ `lunge` คืน `pts` ตัวเดิม

ท่า `lunge` ต้องแยกว่าขาไหนเป็นขาหน้า (ชื่อ key ดู shared_structure ข้อ 1)

1. ทิศที่คนหัน: `facing = (TO_L − HL_L) + (TO_R − HL_R)` (รวมเวกเตอร์ส้น → ปลายเท้าของสองเท้า)
2. `s = 1.0` ถ้า `facing[0] >= 0` ไม่งั้น `s = −1.0`
3. ขาหน้า = ข้างที่ข้อเท้าอยู่ไปทางทิศนั้นมากกว่า: ถ้า `s × A_L.x >= s × A_R.x` ขาหน้าคือ L ไม่งั้นคือ R
4. สร้าง dict ใหม่: `S`, `H` ค่าเดิม และ `Kf Af HLf TOf` จากขาหน้า, `Kb Ab HLb TOb` จากขาหลัง

### `compute_features(ex, Q)`

`Q` อยู่ในพิกัดมาตรฐานแล้ว (หันไปทาง +x, y ชี้ขึ้น) คืน `(np.array([x0, x1, x2]), extra)`

**squat**

| ค่า | วิธีคำนวณ |
|---|---|
| `knee` | `angle_at(K, H, A)` |
| `hip` | `angle_at(H, S, K)` |
| `lean` | `t = S − H`; `comp, proj, perp = projection(t, J)`; `lean = arccos(comp / |t|)` องศา (บีบ [−1, 1]) |

`extra` = `{"torso t": t, "comp_ĵ t": comp, "proj_ĵ t": proj, "ส่วนตั้งฉาก": perp, "เข่าเลยปลายเท้า (เท่าลำตัว)": K.x − TO.x}`

**pushup**

| ค่า | วิธีคำนวณ |
|---|---|
| `elbow` | `angle_at(E, S, W)` |
| `hip_dev` | `body = angle_at(H, S, A)`; `line = S − A`; `cz = cross_z(line, H − A)`; `hip_dev = (180 − body)` คูณ `+1` ถ้า `cz >= 0` ไม่งั้น `−1` |
| `tilt` | `angle_between(line, (1, 0))` |

ลำตัวตรง → `body` = 180° → `hip_dev` = 0 ส่วน cross product บอกว่าสะโพกอยู่ฝั่งไหนของเส้นข้อเท้า → ไหล่: `cz` บวก = อยู่เหนือเส้น (โด่ง), ลบ = อยู่ใต้เส้น (ตก) dot product อย่างเดียวบอกได้แค่ขนาดมุม บอกทิศไม่ได้ จึงต้องใช้ cross product

`extra` = `{"มุมลำตัวที่สะโพก": body, "cross z": cz, "ระยะสะโพกจากเส้น ไหล่-ข้อเท้า": perp}` โดย `perp` มาจาก `projection(H − A, line)`

**lunge**

| ค่า | วิธีคำนวณ |
|---|---|
| `front_knee` | `angle_at(Kf, H, Af)` |
| `shin` | `signed_from_vertical(Kf − Af)` |
| `lean` | `abs(signed_from_vertical(S − H))` |

`extra` = `{"มุมเข่าหลัง": angle_at(Kb, H, Ab), "เข่าหน้าเลยปลายเท้า (เท่าลำตัว)": Kf.x − TOf.x}`

**ตัวอย่างตรวจมือ (squat)**

```
Q:  S(0.8, 0.6)  H(0, 0)  K(0.8, 0)  A(0.4, −0.8)

knee: K→H = (−0.8, 0), K→A = (−0.4, −0.8)   cos = 0.32 / (0.8 × 0.8944) = 0.4472   → 63.43°
hip : H→S = (0.8, 0.6), H→K = (0.8, 0)      cos = 0.64 / (1 × 0.8)      = 0.8      → 36.87°
lean: t = (0.8, 0.6), comp_ĵ t = 0.6, |t| = 1                           cos = 0.6  → 53.13°
```

### `ghost_segments(ex, Q, ref)`

คืน list ของ `(จุดเริ่ม, จุดปลาย)` เป็นเส้นของท่าที่ถูก ในพิกัดมาตรฐาน (งาน C จะแปลงกลับไปพิกัดภาพด้วย M⁻¹) `ref` = features ของท่าต้นแบบ `correct`

เวกเตอร์หนึ่งหน่วยที่เอียงจากแนวตั้งไปข้างหน้า α องศา คือ `(sin α, cos α)`

| ท่า | เส้น |
|---|---|
| `squat` | 1 เส้น: จาก `H` ไป `H + (sin a, cos a)` โดย a = `ref[2]` (มุมโน้มตัวที่ถูก, ลำตัวยาว 1) |
| `pushup` | 2 เส้น: `line = S − A`; `proj` = projection ของ `H − A` บน `line`; สะโพกที่ถูก `hg = A + proj` (จุดบนเส้นไหล่-ข้อเท้าที่ใกล้สะโพกจริงที่สุด) → `(S, hg)` และ `(hg, A)` |
| `lunge` | 2 เส้น: หน้าแข้งที่ถูก จาก `Af` ไป `Af + |Kf − Af| × (sin a, cos a)` โดย a = `ref[1]`; ลำตัวที่ถูก จาก `H` ไป `H + (sin b, cos b)` โดย b = `ref[2]` |

อย่าลืมแปลงองศาเป็นเรเดียน (`math.radians`) ก่อนเข้า `math.sin` / `math.cos`

ทดสอบ

```bash
python check.py angles
```

## เสร็จเมื่อ

- [ ] `python check.py vector` ผ่าน 10/10
- [ ] `python check.py angles` ผ่าน 10/10
- [ ] เปิด pull request และ merge เข้า `main`

## คำถามที่อาจารย์อาจถาม (เตรียมตอบ)

- หามุมจาก dot product ยังไง ทำไมต้องลบด้วยจุดข้อต่อก่อน
- comp กับ proj ต่างกันยังไง ใช้ตรงไหนในโครงงาน
- ทำไมท่าวิดพื้นต้องใช้ cross product เพิ่ม
- Euclidean, Manhattan, Cosine ต่างกันยังไง ทำไมเลือก Euclidean ตัดสิน
