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
from config import CLEAN_LOG, EXERCISES, IMG_EXT, LM, MODEL_PATH, MODEL_URL, NEED, SKIP_REASON, VIS_MIN
from features import prepare_points


def make_landmarker(video=False):
    """ดาวน์โหลดโมเดลถ้ายังไม่มี แล้วคืน (mp, landmarker)"""
    raise NotImplementedError("TODO(D)")


def extract(ex, result, w, h):
    """คืน (ข้าง, จุด, landmarks ทั้ง 33, สถานะ) สถานะ = ok / no_person / low_visibility"""
    raise NotImplementedError("TODO(D)")


def save_row(path, ex, label, side, x, lm):
    """ต่อท้าย 1 แถวใน CSV (สร้างหัวตารางถ้าเป็นไฟล์ใหม่) คอลัมน์ดู docs/shared_structure.md"""
    raise NotImplementedError("TODO(D)")


def log_clean(ex, label, path, status):
    """บันทึกว่าภาพนี้ใช้ได้ (ok) หรือถูกตัดทิ้งเพราะอะไร → ใช้ทำสถิติการ clean ข้อมูล"""
    raise NotImplementedError("TODO(D)")


def draw(img, pts, r):
    """วาดโครงร่าง (เขียว = correct, แดง = อื่น), เส้นท่าที่ถูก (เหลือง) และข้อความผล"""
    raise NotImplementedError("TODO(D)")


def run_image(ex, path, explain, label, save, mp_lmk=None, out_dir=None):
    """ตรวจภาพ 1 ภาพ คืนสถานะ ok / unreadable / no_person / low_visibility / calc_error"""
    raise NotImplementedError("TODO(D)")


def run_folder(ex, folder, explain, label, save):
    """ตรวจทุกภาพในโฟลเดอร์ (ไม่เข้าโฟลเดอร์ย่อย) รูปผลลัพธ์เก็บใน <โฟลเดอร์>/results"""
    raise NotImplementedError("TODO(D)")


def run_camera(ex, cam, save):
    """เปิดกล้อง ตรวจทุกเฟรม ปุ่ม 1/2/3 = บันทึกข้อมูล, e = อธิบาย, q = ออก"""
    raise NotImplementedError("TODO(D)")
