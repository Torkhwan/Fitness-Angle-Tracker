"""
config.py  ค่าคงที่และโครงสร้างข้อมูลที่ทุกคนใช้ร่วมกัน

ไฟล์นี้เขียนเสร็จแล้ว ทุกไฟล์ import จากที่นี่ ห้ามประกาศค่าพวกนี้ซ้ำในไฟล์ตัวเอง
ถ้าจำเป็นต้องแก้ ให้แจ้งในกลุ่มก่อน เพราะกระทบทุกคน (คำอธิบายอยู่ใน docs/data_structure.md)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
             "pose_landmarker_full/float16/latest/pose_landmarker_full.task")
MODEL_PATH = os.path.join(HERE, "pose_landmarker_full.task")
TEMPLATE_PATH = os.path.join(HERE, "templates.json")
TOLERANCE = 10.0  # ต่างจากท่าถูกได้ไม่เกิน ± กี่องศา
VISIBILITY_MIN = 0.5  # visibility ต่ำกว่าค่านี้นับว่าเห็นข้อต่อไม่ชัด
CLEAN_LOG = "clean_log.csv"  # บันทึกทุกภาพที่ป้อนตอนเก็บข้อมูล ว่าใช้ได้หรือตัดทิ้ง
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

# เลขดัชนีข้อต่อของ MediaPipe Pose (33 จุด) แยกข้างซ้ายและข้างขวา
LANDMARK_INDEX = {
    "left":  {"shoulder_point": 11, "elbow_point": 13, "wrist_point": 15, "hip_point": 23,
              "knee_point": 25, "ankle_point": 27, "heel_point": 29, "toe_point": 31},
    "right": {"shoulder_point": 12, "elbow_point": 14, "wrist_point": 16, "hip_point": 24,
              "knee_point": 26, "ankle_point": 28, "heel_point": 30, "toe_point": 32},
}

# ข้อต่อที่แต่ละท่าต้องเห็น
REQUIRED_POINTS = {
    "squat": ["shoulder_point", "hip_point", "knee_point", "ankle_point", "heel_point", "toe_point"],
    "pushup": ["shoulder_point", "elbow_point", "wrist_point", "hip_point", "knee_point", "ankle_point", "toe_point"],
    "lunge": ["shoulder_point", "hip_point", "knee_point", "ankle_point"],
}

# สถานะของภาพที่ใช้ไม่ได้ → ข้อความที่พิมพ์
SKIP_REASON = {"unreadable": "เปิดไฟล์ภาพไม่ได้", "no_person": "ไม่พบคนในภาพ",
               "low_visibility": "เห็นข้อต่อไม่ชัด (ถ่ายด้านข้างให้เห็นทั้งตัวถึงปลายเท้า)",
               "calc_error": "คำนวณไม่ได้ (เช่น แนวพื้นยาว 0)"}

#
# ตั้งค่าแต่ละท่า
#   thai_name: ชื่อท่าภาษาไทย
#   angles   : มุม 3 ค่าที่วัดจากท่านั้น
#              (ชื่อ, ชื่อไทย, ข้อความเมื่อ "มากกว่า" ท่าถูก, ข้อความเมื่อ "น้อยกว่า" ท่าถูก)
#              {difference} ในข้อความ = จำนวนองศาที่ต่างจากท่าถูก
#   templates: ค่าสมมติ จะถูกแทนด้วยค่าเฉลี่ยจากข้อมูลจริงผ่าน --build-templates
#   labels   : ชื่อ label → ข้อความไทย
#   gate     : ประเมินท่าเฉพาะตอนที่อยู่ในช่วงลงท่า (ใช้กับกล้อง)
#   lines    : คู่ข้อต่อที่ลากเส้นโครงร่าง
#
EXERCISES = {
    "squat": {
        "thai_name": "สควอต",
        "angles": [
            ("knee", "มุมเข่า", "ย่อเข่ายังไม่พอ {difference:.0f}° → ย่อลงให้ต้นขาขนานพื้น",
             "ย่อลึกกว่าท่าต้นแบบ {difference:.0f}°"),
            ("hip", "มุมสะโพก", "", ""),
            ("lean", "มุมโน้มตัว", "ลำตัวโน้มไปข้างหน้ามากเกินไป {difference:.0f}° → ยืดอก ดันสะโพกไปด้านหลัง",
             "ลำตัวตั้งตรงเกินไป {difference:.0f}° → โน้มตัวไปข้างหน้าเล็กน้อย"),
        ],
        "templates": {"correct": [65, 55, 35], "lean_forward": [65, 35, 55], "shallow": [120, 110, 20]},
        "labels": {"correct": "ท่าถูกต้อง", "lean_forward": "หลังโน้มไปข้างหน้ามากเกินไป", "shallow": "ย่อไม่พอ"},
        "gate": lambda angle_values: angle_values[0] < 130,
        "lines": [("shoulder_point", "hip_point"), ("hip_point", "knee_point"), ("knee_point", "ankle_point"),
                  ("ankle_point", "heel_point"), ("heel_point", "toe_point"), ("ankle_point", "toe_point")],
    },
    "pushup": {
        "thai_name": "วิดพื้น",
        "angles": [
            ("elbow", "มุมศอก", "งอศอกไม่พอ {difference:.0f}° → ลดตัวลงให้ต่ำกว่านี้",
             "ลงต่ำกว่าท่าต้นแบบ {difference:.0f}°"),
            ("hip_deviation", "สะโพกเบี่ยงจากแนวลำตัว", "สะโพกโด่งขึ้น {difference:.0f}° → ลดสะโพกให้ลำตัวเป็นเส้นตรง",
             "สะโพกตก {difference:.0f}° → เกร็งหน้าท้อง ยกสะโพกให้ลำตัวเป็นเส้นตรง"),
            ("tilt", "มุมลำตัวกับพื้น", "", ""),
        ],
        "templates": {"correct": [90, 0, 5], "shallow": [130, 0, 20], "hip_sag": [90, -20, 5]},
        "labels": {"correct": "ท่าถูกต้อง", "shallow": "งอศอกไม่พอ", "hip_sag": "สะโพกตก"},
        "gate": lambda angle_values: angle_values[0] < 150,
        "lines": [("shoulder_point", "elbow_point"), ("elbow_point", "wrist_point"), ("shoulder_point", "hip_point"),
                  ("hip_point", "knee_point"), ("knee_point", "ankle_point"), ("ankle_point", "toe_point")],
    },
    "lunge": {
        "thai_name": "ลันจ์",
        "angles": [
            ("front_knee", "มุมเข่าหน้า", "ย่อยังไม่พอ {difference:.0f}° → ลดตัวลงให้เข่าหน้าตั้งฉาก", ""),
            ("shin", "มุมหน้าแข้งหน้า",
             "เข่าหน้าล้ำปลายเท้า {difference:.0f}° → ก้าวเท้ายาวขึ้น ให้เข่าอยู่เหนือข้อเท้า", ""),
            ("lean", "มุมโน้มตัว", "ลำตัวโน้มไปข้างหน้า {difference:.0f}° → ยืดตัวตรง", ""),
        ],
        "templates": {"correct": [90, 10, 5], "knee_over_toe": [80, 35, 5], "torso_lean": [95, 10, 30]},
        "labels": {"correct": "ท่าถูกต้อง", "knee_over_toe": "เข่าล้ำปลายเท้า", "torso_lean": "ลำตัวโน้ม/เอียง"},
        "gate": lambda angle_values: angle_values[0] < 140,
        "lines": [("shoulder_point", "hip_point"), ("hip_point", "front_knee_point"),
                  ("front_knee_point", "front_ankle_point"), ("front_ankle_point", "front_heel_point"),
                  ("front_heel_point", "front_toe_point"), ("hip_point", "back_knee_point"),
                  ("back_knee_point", "back_ankle_point"), ("back_ankle_point", "back_toe_point")],
    },
}
