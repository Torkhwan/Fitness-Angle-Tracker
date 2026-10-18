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
    
    # Support Thai name folder path
    with open(MODEL_PATH, "rb") as model_file:
        model_buffer = model_file.read()

    # setting
    options = vision.PoseLandmarkerOptions(
        base_options=mediapipe_python.BaseOptions(model_asset_buffer=model_buffer),
        running_mode=mode,
        # detected 1 person only
        num_poses=1,
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
        lm = pose_landmarks[landmark_idx]
        # return numpy array
        return np.array([lm.x * width, lm.y * height])
    
    # get points name form config.py
    required_points = REQUIRED_POINTS[exercise]
    
    # check left/right side 
    vis_score = {}
    for side_name in ('left', 'right'):
        scores = [pose_landmarks[LANDMARK_INDEX[side_name][pt]].visibility for pt in required_points]
        vis_score[side_name] = sum(scores) / len(scores)
    # select side
    side = 'left' if vis_score['left'] >= vis_score['right'] else 'right'
    
    # check low visibility
    if vis_score[side] < VISIBILITY_MIN:
        return None, None, None, "low_visibility"

    # squat, push-up use side view
    points = {}
    if exercise in ('squat', 'pushup'):
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
    is_new_file = not os.path.exists(CLEAN_LOG)

    # prepare data
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    image_name = os.path.basename(path)
    header = ["time", "exercise", "label", "image", "status"]
    row = [current_time, exercise, label, image_name, status]
    
    # write file
    with open(CLEAN_LOG, mode='a', newline='', encoding='utf-8') as file:
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
        # cv2.putText(img, text, org, fontFace, fontScale, color, thickness=1, lineType=cv2.LINE_8)
        cv2.putText(image, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_BLACK, thickness=5)
        # text main color
        cv2.putText(image, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.75, main_color, thickness=2)
    
    return image

def run_image(exercise: str, path: str, explain: bool, label: str | None, save: str | None,
              landmarker_pair: tuple | None = None, output_folder: str | None = None) -> str:
    """ตรวจภาพ 1 ภาพ คืนสถานะ ok / unreadable / no_person / low_visibility / calc_error"""
    import cv2  

    # prepare model
    mediapipe, landmarker = landmarker_pair or make_landmarker(video=False)

    # read imgae file
    image = cv2.imread(path)
    if image is None:
        status = "unreadable"
    else:
        # image size
        height, width = image.shape[:2]

        # convert BGR to RGB and send to mediapipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mediapipe.Image(image_format=mediapipe.ImageFormat.SRGB, data=image_rgb)
        detection = landmarker.detect(mp_image)
        
        # get position poits and side
        side, points, landmarks, status = extract(exercise, detection, width, height)
        
        # check status and anlyze
        if status == "ok":
            try:
                result = analyze(exercise, points, explain=explain)
            except (ValueError, ZeroDivisionError):
                status = "calc_error" 
        
    # save history in clean_log
    if label:
        log_clean(exercise, label, path, status)
    
    # stop if image not ok  
    image_name = os.path.basename(path)
    if status != "ok":
        print(f"ข้าม {image_name}: {SKIP_REASON[status]}")
        return status

    # show analyze result
    print(f"[{image_name}] ใช้ข้าง: {side}")
    print_result(result)
    
    # save angle and position data to CSV
    if label:
        csv_path = save or f"data_{exercise}.csv"
        save_row(csv_path, exercise, label, side, result["angle_values"], landmarks)
    
    # draw and save new image
    base_name = os.path.splitext(image_name)[0]
    output_filename = f"{base_name}_result.jpg"
    
    # if folder create folder if not exist
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, output_filename)
    else:
        output_path = os.path.join(os.path.dirname(path), output_filename)

    # draw and save image
    annotated_image = draw(image, points, result)
    cv2.imwrite(output_path, annotated_image)
    print("บันทึกรูปผลลัพธ์:", output_path)

    return status
    
def run_folder(exercise: str, folder: str, explain: bool, label: str | None, save: str | None) -> None:
    """ตรวจทุกภาพในโฟลเดอร์ (ไม่เข้าโฟลเดอร์ย่อย) รูปผลลัพธ์เก็บใน <โฟลเดอร์>/results"""
    # serch image files in folder
    image_files = sorted(
                file_name for file_name in os.listdir(folder)
                if file_name.lower().endswith(IMAGE_EXTENSIONS)
            )
    # if not found image files, exit
    if not image_files:
            sys.exit(f"ไม่พบไฟล์ภาพใน {folder}")
    
    # create landmarker
    landmarker_pair = make_landmarker(video=False)  
    
    # create output folder
    output_folder = os.path.join(folder, "results")
    
    # check status and count 
    status_counts = {}
    for file_name in image_files:
        image_path = os.path.join(folder, file_name)
        status = run_image(
            exercise=exercise,
            path=image_path,
            explain=explain,
            label=label,
            save=save,
            landmarker_pair=landmarker_pair,
            output_folder=output_folder
        )
        # count status
        status_counts[status] = status_counts.get(status, 0) + 1

        # print summary
        summary_parts = [f"ใช้ได้ {status_counts.get('ok', 0)}"]
        for status, count in status_counts.items():
            if status != "ok":
                summary_parts.append(f"{SKIP_REASON[status]} {count}")

    print(f"\nสรุป {len(image_files)} ภาพ: " + ", ".join(summary_parts))

ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fat.ico")
# short keys for switching exercise while the camera is running
SWITCH_KEYS = {ord("s"): "squat", ord("p"): "pushup", ord("l"): "lunge"}

def set_window_icon(window_title: str) -> None:
    """ใส่ไอคอน fat.ico ให้หน้าต่างและ taskbar (Windows เท่านั้น ระบบอื่นข้ามไป)"""
    if sys.platform != "win32" or not os.path.exists(ICON_PATH):
        return
    import ctypes
    user32 = ctypes.windll.user32
    user32.FindWindowW.restype = ctypes.c_void_p
    user32.LoadImageW.restype = ctypes.c_void_p
    user32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]
    # separate taskbar group from python.exe so the taskbar shows our icon
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FAT.PoseCoach")
    window = user32.FindWindowW(None, window_title)
    # 1 = IMAGE_ICON, 0x10 = LR_LOADFROMFILE
    icon_big = user32.LoadImageW(None, ICON_PATH, 1, 256, 256, 0x10)
    icon_small = user32.LoadImageW(None, ICON_PATH, 1, 32, 32, 0x10)
    if window and icon_big and icon_small:
        # 0x80 = WM_SETICON, 1 = ICON_BIG, 0 = ICON_SMALL
        user32.SendMessageW(window, 0x80, 1, icon_big)
        user32.SendMessageW(window, 0x80, 0, icon_small)

def camera_mode(exercise: str) -> tuple:
    """คืน (ชื่อหน้าต่าง, ปุ่ม 1/2/3 → label) ของท่านี้ และพิมพ์วิธีใช้ใน Terminal"""
    labels = list(EXERCISES[exercise]["templates"])
    key_to_label = {ord(str(index + 1)): label for index, label in enumerate(labels)}
    key_guides = " ".join(f"{index + 1}={label}" for index, label in enumerate(labels))
    print(f"[{EXERCISES[exercise]['thai_name']}] หันข้างให้กล้องเห็นทั้งตัว | "
            f"{key_guides} (เก็บข้อมูล) | s/p/l=สลับท่า | e=อธิบาย | q=ออก")
    return f"FAT Pose Coach - {exercise}", key_to_label

def run_camera(exercise: str, camera_index: int, save: str | None) -> None:
    """เปิดกล้อง ตรวจทุกเฟรม ปุ่ม 1/2/3 = บันทึกข้อมูล, s/p/l = สลับท่า, e = อธิบาย, q = ออก"""
    import cv2

    # prepare model
    mediapipe, landmarker = make_landmarker(video=True)
    # open camera
    camera = cv2.VideoCapture(camera_index)
    # cannot open
    if not camera.isOpened():
        sys.exit(f"เปิดกล้องไม่ได้ (กล้องหมายเลข {camera_index})")

    # --save is for the starting exercise only (other exercises go to data_<exercise>.csv)
    start_exercise = exercise
    window_title, key_to_label = camera_mode(exercise)

    # resizable window (drag or maximize), bigger default size
    # window_name stays the same, only the title bar text changes when switching exercise
    window_name = "FAT Pose Coach"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 960)
    cv2.setWindowTitle(window_name, window_title)
    set_window_icon(window_title)

    # save start time 
    start_time = time.time()
    # last timestamp in ms
    last_timestamp_ms = -1
    
    while True:
        frame_ok, frame = camera.read()
        if not frame_ok:
            print("ไม่สามารถอ่านภาพจากกล้องได้")
            break
        # prepare last frame data for save
        last_frame = None
        height, width = frame.shape[:2]

        # calculate timestamp in milliseconds since start
        timestamp_ms = int((time.time() - start_time) * 1000)
        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1
        last_timestamp_ms = timestamp_ms

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mediapipe.Image(image_format=mediapipe.ImageFormat.SRGB, data=image_rgb)

        # detect position for the current frame
        detection = landmarker.detect_for_video(mp_image, timestamp_ms)
        side, points, landmarks, _ = extract(exercise, detection, width, height)

        # analyze and draw results if points are detected
        if points is not None:
            try:
                result = analyze(exercise, points)
                # save last frame data
                last_frame = {
                    "side": side,
                    "points": points,
                    "landmarks": landmarks,
                    "result": result
                }
                # check if the person is in the correct position
                is_in_position = EXERCISES[exercise]["gate"](result["angle_values"])
                if is_in_position:
                    frame = draw(frame, points, result)
                else:
                    cv2.putText(frame, "go down into the position", (15, 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            # if error skip
            except (ValueError, ZeroDivisionError):
                pass  
        else:
            # if not found person or low visibility, show message
            cv2.putText(frame, "show your full body from the side", (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # show exercise label
        exercise_label = f"{exercise.upper()}"
        cv2.putText(frame, exercise_label, (width - 90, height - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), thickness=8)
        
        cv2.putText(frame, exercise_label, (width - 90, height - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), thickness=8)
        
        # show video
        cv2.imshow(window_name, frame)

        # wait for key press
        pressed_key = cv2.waitKey(1) & 0xFF

        # 'q' = quit form program
        if pressed_key == ord("q"):
            break

        # s/p/l = switch exercise without restarting
        if pressed_key in SWITCH_KEYS and SWITCH_KEYS[pressed_key] != exercise:
            exercise = SWITCH_KEYS[pressed_key]
            window_title, key_to_label = camera_mode(exercise)
            cv2.setWindowTitle(window_name, window_title)
            continue

        # wait short key to save data
        if last_frame and pressed_key in key_to_label:
            target_label = key_to_label[pressed_key]
            csv_path = (save if save and exercise == start_exercise else None) or f"data_{exercise}.csv"
            save_row(csv_path, exercise, target_label, last_frame["side"],
                        last_frame["result"]["angle_values"], last_frame["landmarks"])

        # e = explain
        if last_frame and pressed_key == ord("e"):
            analyze(exercise, last_frame["points"], explain=True)
            print_result(last_frame["result"])

    # release camera and close windows
    camera.release()
    cv2.destroyAllWindows()