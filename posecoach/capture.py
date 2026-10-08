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
        
def extract(exercise, detection, width, height):
    """detection = ผลตรวจจับของ MediaPipe, width/height = ขนาดภาพ
    คืน (side, points, landmarks ทั้ง 33, status)  status = ok / no_person / low_visibility"""
    raise NotImplementedError("TODO(D)")


def save_row(path, exercise, label, side, angle_values, landmarks):
    """ต่อท้าย 1 แถวใน CSV (สร้างหัวตารางถ้าเป็นไฟล์ใหม่) คอลัมน์ดู docs/shared_structure.md"""
    raise NotImplementedError("TODO(D)")


def log_clean(exercise, label, path, status):
    """บันทึกว่าภาพนี้ใช้ได้ (ok) หรือถูกตัดทิ้งเพราะอะไร → ใช้ทำสถิติการ clean ข้อมูล"""
    raise NotImplementedError("TODO(D)")


def draw(image, points, result):
    """วาดโครงร่าง (เขียว = correct, แดง = อื่น), เส้นท่าที่ถูก (เหลือง) และข้อความผล"""
    raise NotImplementedError("TODO(D)")


def run_image(exercise, path, explain, label, save, landmarker_pair=None, output_folder=None):
    """ตรวจภาพ 1 ภาพ คืนสถานะ ok / unreadable / no_person / low_visibility / calc_error"""
    raise NotImplementedError("TODO(D)")


def run_folder(exercise, folder, explain, label, save):
    """ตรวจทุกภาพในโฟลเดอร์ (ไม่เข้าโฟลเดอร์ย่อย) รูปผลลัพธ์เก็บใน <โฟลเดอร์>/results"""
    raise NotImplementedError("TODO(D)")


def run_camera(exercise, camera_index, save):
    """เปิดกล้อง ตรวจทุกเฟรม ปุ่ม 1/2/3 = บันทึกข้อมูล, e = อธิบาย, q = ออก"""
    raise NotImplementedError("TODO(D)")
