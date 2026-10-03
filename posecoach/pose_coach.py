"""
Pose Coach  ตรวจท่าออกกำลังกาย 3 ท่า (Squat / Push-up / Lunge) ด้วยเวกเตอร์และเมทริกซ์

ถ่ายจากด้านข้าง เห็นทั้งตัวถึงปลายเท้า
MediaPipe ใช้แค่ดึงพิกัดข้อต่อ ส่วนการคำนวณทั้งหมดเขียนเอง

  python pose_coach.py --selftest
  python pose_coach.py --exercise squat  --camera 0
  python pose_coach.py --exercise pushup --image pushup.jpg --explain
  python pose_coach.py --exercise lunge  --image lunge.jpg --label correct --save data_lunge.csv
  python pose_coach.py --exercise squat  --image photos/squat_correct --label correct   # ทั้งโฟลเดอร์
  python pose_coach.py --build-templates data_squat.csv data_pushup.csv data_lunge.csv
  python pose_coach.py --evaluate data_squat.csv

ไฟล์นี้  งาน D: main() รับคำสั่งแล้วส่งต่อให้ฟังก์ชันของแต่ละงาน (docs/role_D_capture.md)
"""
import argparse
import os
import sys

from capture import run_camera, run_folder, run_image
from config import EXERCISES
from dataset import build_templates, evaluate
from selftest import selftest


def main():
    raise NotImplementedError("TODO(D)")


if __name__ == "__main__":
    main()
