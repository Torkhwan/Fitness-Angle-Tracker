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

ไฟล์นี้  งาน D: main() รับคำสั่งแล้วส่งต่อให้ฟังก์ชันของแต่ละงาน (docs/capture.md)
"""
import argparse
import os
import sys

from capture import run_camera, run_folder, run_image
from config import EXERCISES
from dataset import build_templates, evaluate
from selftest import selftest


def main():
    """อ่านตัวเลือกจากคำสั่ง แล้วเรียกฟังก์ชันที่ตรงกับคำสั่งนั้น"""
    # create obj
    parser = argparse.ArgumentParser(description="Pose Coach - Squat / Push-up / Lunge")
    # select exercise 
    parser.add_argument("--exercise", choices=list(EXERCISES), default="squat")
    # 
    parser.add_argument('--selftest', action='store_true')
    # image file or folder to process
    parser.add_argument('--image', help='ไฟล์ภาพ หรือโฟลเดอร์ภาพ')
    # camera index
    parser.add_argument('--camera', type=int, help='กล้องที่ใช้ (0, 1, 2, ...)')
    # explain the result
    parser.add_argument('--explain', action='store_true')
    # label for the image
    parser.add_argument('--label')
    # add file name to save the result
    parser.add_argument("--save", help='ไฟล์ CSV (ค่าเริ่มต้น data_<exercise>.csv)')
    # build templates from CSV files
    parser.add_argument("--build-templates", metavar='CSV', nargs='+')
    # evaluate CSV file
    parser.add_argument("--evaluate", metavar='CSV', nargs='+')
    # setting test ratio
    parser.add_argument("--test-ratio", type=float, default=0.2, help='สัดส่วนข้อมูลทดสอบ (ค่าเริ่มต้น 0.2, 0 = ใช้ท่าต้นแบบจริงใน templates.json ทายทุกแถว)')

    # get all params to process
    arguments = parser.parse_args()
    
    # if not label exit
    if arguments.label and arguments.label not in EXERCISES[arguments.exercise]['templates']:
      sys.exit(f"--label ของ {arguments.exercise} ต้องเป็น: {', '.join(EXERCISES[arguments.exercise]['templates'])}")
    
    # check run selftest
    if arguments.selftest:
      # run selftest if pass exit code 0 else 1
      sys.exit(0 if selftest() else 1)
    
    # check run build templates
    if arguments.build_templates:
      return build_templates(arguments.build_templates)
    
    # check run evaluate
    if arguments.evaluate:
      return evaluate(arguments.evaluate, test_ratio=arguments.test_ratio)
    
    # if image is provided and is path a folder?
    if arguments.image and os.path.isdir(arguments.image):
      # run folder
      return run_folder(arguments.exercise, arguments.image, arguments.explain, arguments.label, arguments.save)
    if arguments.image:
      # run image
      status = run_image(arguments.exercise, arguments.image, arguments.explain, arguments.label, arguments.save)
      sys.exit(0 if status == "ok" else 1)
    
    # if camera index is provided
    if arguments.camera is not None:
      return run_camera(arguments.exercise, arguments.camera, arguments.save)

    # if not any of conditions, print help
    parser.print_help()
    
if __name__ == "__main__":
    main()
