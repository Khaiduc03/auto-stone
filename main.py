import cv2  # Thư viện OpenCV dùng để xử lý ảnh
import numpy as np  # Thư viện numpy hỗ trợ thao tác mảng
import time  # Thư viện đo thời gian
import random
import math
#from typing import Tuple, Dict, Any, Optional  # Khai báo kiểu dữ liệu
from character_utils import detect_characters_group_bbox
from detect_utils import detect_template
from sovle_quiz import find_search_user ,get_search_user,sovle_capcha,sovle_capchav2
import uiautomator2 as u2
from constants import (
DEVICE_ID,
TEMPLATE_PATH,
GRASS_ROI,
SAVE_IMAGE,
OUTPUT_PATH,
CAPTCHA_TEMPLATE,
CAPTCHA_ROI
)
def adb_tap_random_circle(x, y, radius=10, device_id=None):
    # Tạo điểm ngẫu nhiên trong hình tròn
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.uniform(0, 1))  # sqrt để phân bố đều
    dx = int(r * math.cos(angle))
    dy = int(r * math.sin(angle))

    rx, ry = x + dx, y + dy

    # Gửi lệnh tap
    cmd = ["adb"]
    if device_id:
        cmd += ["-s", device_id]
    cmd += ["shell", "input", "tap", str(rx), str(ry)]
    subprocess.run(cmd)

def uiauto_tap(x, y, radius=15, device_ip="127.0.0.1"):
    # Random điểm trong bán kính
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.uniform(0, 1))
    dx = int(r * math.cos(angle))
    dy = int(r * math.sin(angle))

    rx, ry = x + dx, y + dy

    # Delay nhỏ để giả lập thao tác người
    time.sleep(random.uniform(0.2, 0.8))

    # Kết nối và tap
    d = u2.connect(device_ip)
    d.click(rx, ry)
def adb_screencap(device_id=None):
    # Chụp màn hình qua ADB và giải mã thành ảnh OpenCV
    cmd = ["adb"] + (
        ["-s", device_id] if device_id else []
    ) + ["exec-out", "screencap", "-p"]
    raw = subprocess.check_output(cmd)
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        print("Lỗi giải mã ảnh ADB", file=sys.stderr)
        sys.exit(1)
    return img

def tap_capcha(device_id=None):
    full_img = adb_screencap()
    idx = sovle_capchav2(full_img)
    match idx:
        case 1:
            uiauto_tap(160, 1656, 10, DEVICE_ID)
        case 2:
            uiauto_tap(400, 1656, 10, DEVICE_ID)
        case 3:
            uiauto_tap(635, 1656, 10, DEVICE_ID)
        case 4:
            uiauto_tap(855, 1656, 10, DEVICE_ID)

def is_captcha_present(image):
    try:
        _, info = detect_template(image, CAPTCHA_TEMPLATE, CAPTCHA_ROI)
        print(f"[CAPTCHA] Đã phát hiện tại {info['top_left']}, score: {info['match_score']:.2f}")
        return True
    except Exception:
        return False


def monitor_loop(device_id, interval_sec=1.5):
    print(f"[Giám sát] Bắt đầu theo dõi {device_id}...")
    while True:
        try:
            # uiauto_tap(78, 1656, DEVICE_ID)
            screen = adb_screencap(device_id=device_id)
            if is_captcha_present(screen):
                print(f"[{device_id}] ✓ Đã phát hiện CAPTCHA")
                tap_capcha(device_id)
                #time.sleep(2)  # Đợi sau khi xử lý captcha
            else:
                print(f"[{device_id}] ✓ Không phát hiện CAPTCHA")
        except Exception as e:
            print(f"[{device_id}] Lỗi: {e}")
        time.sleep(interval_sec)


if __name__ == "__main__":
    import subprocess
    import sys
   # start_time = time.time()  # Bắt đầu đo tổng thời gian
    monitor_loop(DEVICE_ID, interval_sec=1)  # Bắt đầu giám sát
    


    # # In tổng thời gian
    # print(f"Tổng thời gian: {time.time() - start_time:.2f} giây")
