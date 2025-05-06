import subprocess
import sys
import cv2  # Thư viện OpenCV dùng để xử lý ảnh
import numpy as np  # Thư viện numpy hỗ trợ thao tác mảng
import time  # Thư viện đo thời gian

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
    return img

def get_connected_devices():
    result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = result.stdout.strip().split("\n")[1:]  # bỏ dòng đầu "List of devices attached"
    device_ids = [line.split()[0] for line in lines if "device" in line]
    return device_ids


# def monitor_loop(device_id, interval_sec=1.5):
#     print(f"[Giám sát] Bắt đầu theo dõi {device_id}...")
#     while True:
#         try:
#             # uiauto_tap(78, 1656, DEVICE_ID)
#             screen = adb_screencap(device_id=device_id)
#             if is_captcha_present(screen):
#                 print(f"[{device_id}] ✓ Đã phát hiện CAPTCHA")
#                 tap_capcha(device_id, full_img=screen)
#                 #time.sleep(2)  # Đợi sau khi xử lý captcha
#             else:
#                 print(f"[{device_id}] ✓ Không phát hiện CAPTCHA")
#         except Exception as e:
#             print(f"[{device_id}] Lỗi: {e}")
#         time.sleep(interval_sec)

