"""
capture.py  งาน D: รับภาพ/กล้อง → ดึงพิกัดด้วย MediaPipe → บันทึกข้อมูล → วาดผล

คำอธิบายงาน: docs/role_D_capture.md
MediaPipe ใช้แค่ดึงพิกัดข้อต่อ การคำนวณทั้งหมดอยู่ในไฟล์ของงาน A, B, C
import cv2 และ mediapipe ไว้ "ในฟังก์ชัน" เพื่อให้ selftest รันได้โดยไม่ต้องโหลดสองตัวนี้
"""
import csv
import os
import sys
import time
import urllib.request

import numpy as np

from analyze import analyze, print_result
from angles import prepare_points
from config import (CLEAN_LOG, EXERCISES, IMAGE_EXTENSIONS, LANDMARK_INDEX, MODEL_PATH, MODEL_URL,
                    REQUIRED_POINTS, SKIP_REASON, VISIBILITY_MIN)

def make_landmarker(video:bool = False) -> tuple: 
    """ดาวน์โหลดโมเดลถ้ายังไม่มี แล้วคืน (mediapipe, landmarker)"""
    import mediapipe 
    from mediapipe.tasks import python as mediapipe_python
    from mediapipe.tasks.python import vision
    
    # check have model?
    if not os.path.exists(MODEL_PATH):
        print(f'กำลังดาวน์โหลดโมเดล {MODEL_URL} → {MODEL_PATH} ...')
        # download model
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        
    # select mode
    mode = vision.RunningMode.VIDEO if video else vision.RunningMode.IMAGE
    
    # setting
    options = vision.PoseLandmarkerOptions(
        # where is the model file
        base_options = mediapipe_python.BaseOptions(model_asset_path=MODEL_PATH),
        # which mode to run 
        running_mode = mode,
        # focus one person only
        num_poses = 1
    )
    
    return mediapipe, vision.PoseLandmarker.create_from_options(options)
        
def extract(exercise: str, detection, width: int, height: int) -> tuple:
    """
    detection = ผลตรวจจับของ MediaPipe, width/height = ขนาดภาพ
    คืน (side, points, landmarks ทั้ง 33, status)  status = ok / no_person / low_visibility
    """
    # check person in image , pose_landmarks = list person detected, if no person detected return []
    if not detection.pose_landmarks or len(detection.pose_landmarks) == 0:
        return None, None, None, "no_person"

    # get first person detected
    pose_landmarks = detection.pose_landmarks[0]
    
    # helper function convert landmark to pixel coordinates
    def to_pixel(landmark_idx):
        lm = landmark_idx
        # return numpy array
        return np.array([lm.x * width, lm.y * height])
    
    # get points name form config.py
    required_points = REQUIRED_POINTS[exercise]
    
    # check left/right side 
    vis_score = {}
    for side_name in ('left', 'right'):
        scores = [landmark[LANDMARK_INDEX[side_name][pt]].visibility for pt in required_points]
        vis_score[side_name] = sum(scores) / len(scores)
    # select side
    side = 'left' if vis_score['left'] >= vis_score['right'] else 'right'
    
    # check low visibility
    if vis_score[side] < VISIBILITY_MIN:
        return None, None, None, "low_visibility"

    # squat, push-up use side view
    points = {}
    if exercise in ('squat', 'push-up'):
        for pt in required_points:
            idx = LANDMARK_INDEX[side][pt]
            points[pt] = to_pixel(idx)
            
    # lunge use two legs front leg points and back leg points
    elif exercise == 'lunge':
        points['shoulder_point'] = to_pixel(LANDMARK_INDEX[side]['shoulder_point'])
        points['hip_point'] = to_pixel(LANDMARK_INDEX[side]['hip_point'])
        for s in ('left', 'right'):
            for pt in ('knee_point', 'ankle_point', 'heel_point', 'toe_point'):
                idx = LANDMARK_INDEX[s][pt]
                points[f'{s}_{pt}'] = to_pixel(idx)

    # prepare_points: ฟังก์ชันสำหรับจัดระเบียบจุด
    points = prepare_points(exercise, points)
    return side, points, pose_landmarks, "ok"

def save_row(path: str, exercise: str, label: str, side: str, angle_values: np.ndarray, landmarks: list) -> None:
    """ต่อท้าย 1 แถวใน CSV (สร้างหัวตารางถ้าเป็นไฟล์ใหม่) คอลัมน์ดู docs/shared_structure.md"""
    # check have file?
    is_new_file = not os.path.exists(path)
    
    # get angle names 
    angle_names = [name for name, *_ in EXERCISES[exercise]['angles']]
    
    # open file mode = append
    with open(path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # write header if new file
        if is_new_file:
            header = (
                ["time", "exercise", "label", "side", *angle_names]
                + [f"{axis}{index}" for index in range(33) for axis in ("x", "y")]
                + [f"v{index}" for index in range(33)]
            )
            writer.writerow(header)
            
        # write row
        row = (
            [
                time.strftime("%Y-%m-%d %H:%M:%S"),
                exercise,
                label,
                side,
                *[f"{value:.3f}" for value in angle_values], 
            ]
            # พิกัด x, y
            + [f"{coordinate:.5f}" for landmark in landmarks for coordinate in (landmark.x, landmark.y)]
            # ค่า visibility
            + [f"{landmark.visibility:.3f}" for landmark in landmarks]
        )
        # write row
        writer.writerow(row)

    print(f"บันทึก {exercise}/{label} ลง {path}")
    
def log_clean(exercise: str, label: str, path: str, status: str) -> None:
    """บันทึกว่าภาพนี้ใช้ได้ (ok) หรือถูกตัดทิ้งเพราะอะไร → ใช้ทำสถิติการ clean ข้อมูล"""
    # check have file?
    is_new_file = not os.path.exists(path)

    # prepare data
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    image_name = os.path.basename(path
    header = ["time", "exercise", "label", "image", "status"]
    row = [current_time, exercise, label, image_name, status])
    
    # write file
    with open(CLEAN_LOG, mode='a', new_line='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # write header if new file
        if is_new_file:
            writer.writerow(header)
        # write row
        writer.writerow(row)

def draw(image: np.ndarray, points: dict, result: dict) -> np.ndarray:
    """วาดโครงร่าง (เขียว = correct, แดง = อื่น), เส้นท่าที่ถูก (เหลือง) และข้อความผล"""
    import cv2
    
    # define colors
    COLOR_GREEN = (0, 200, 0)
    COLOR_RED = (0, 0, 255)
    COLOR_WHITE = (255, 255, 255)
    COLOR_YELLOW = (0, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    
    # define correct, incorrect color
    best_label = result['ranking'][0]['name']
    main_color = COLOR_GREEN if best_label == 'correct' else COLOR_RED
    
    # convert (x, y) float to int 
    def to_pixel(point):
        return (int(point[0]), int(point[1]))
    
    # draw skeleton lines
    exercise_name = result['exercise']
    for start_name, end_name in EXERCISES[exercise_name]['lines']:
        # find position
        start_pos = to_pixel(points[start_name])
        end_pos = to_pixel(points[end_name])
        # draw line
        cv2.line(image, start_pos, end_pos, main_color, thickness=4)
    
    # draw point 
    for point in points.values():
        cv2.circle(image, to_pixel(point), radius=6, color=COLOR_WHITE, thickness=-1)

    # draw correct pose lines
    for start, end in result["ghosts"]:
        cv2.line(image, to_pixel(start), to_pixel(end), COLOR_YELLOW, thickness=3)
        cv2.circle(image, to_pixel(end), radius=7, color=COLOR_YELLOW, thickness=2)
        
    # prepare text
    angle_names = [name for name, *_ in EXERCISES[exercise_name]["angles"]]
    angles_str = "  ".join(f"{name} {val:.0f}" for name, val in zip(angle_names, result["angle_values"]))
    distance = result["ranking"][0]["euclidean"]
    
    text_lines = [
            angles_str,                                              
            f"{exercise_name}: {best_label} (distance={distance:.1f})",  
            "yellow = correct form"                                  
            ]
    
    # draw text in Left Top corner
    for index, text in enumerate(text_lines):
        text_pos = (15, 35 + (32 * index))
        # border black
        cv2.putText(image, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_BLACK, thickness=5)
        # text main color
        cv2.putText(image, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, main_color, thickness=2)
    
    return image

def run_image(exercise: str, path: str, explain: bool, label: str | None, save: str | None,
              landmarker_pair: tuple | None = None, output_folder: str | None = None) -> str:
    """ตรวจภาพ 1 ภาพ คืนสถานะ ok / unreadable / no_person / low_visibility / calc_error"""
    raise NotImplementedError("TODO(D)")

def run_folder(exercise: str, folder: str, explain: bool, label: str | None, save: str | None) -> None:
    """ตรวจทุกภาพในโฟลเดอร์ (ไม่เข้าโฟลเดอร์ย่อย) รูปผลลัพธ์เก็บใน <โฟลเดอร์>/results"""
    raise NotImplementedError("TODO(D)")

def run_camera(exercise: str, camera_index: int, save: str | None) -> None:
    """เปิดกล้อง ตรวจทุกเฟรม ปุ่ม 1/2/3 = บันทึกข้อมูล, e = อธิบาย, q = ออก"""
    raise NotImplementedError("TODO(D)")
