import subprocess
import sys
import cv2  # Thư viện OpenCV dùng để xử lý ảnh
import numpy as np  # Thư viện numpy hỗ trợ thao tác mảng
import time  # Thư viện đo thời gian
import uiautomator2 as u2
def adb_screencap(device_id=None):
    # Kết nối đến thiết bị Android qua uiautomator2
    # Nếu device_id là None thì sẽ connect đến thiết bị mặc định
    d = u2.connect_usb(device_id) if device_id else u2.connect()
    
    # Chụp màn hình dưới dạng OpenCV BGR ndarray
    img = d.screenshot(format="opencv")
    if img is None:
        print("Lỗi giải mã ảnh uiautomator2", file=sys.stderr)
    return img

def get_connected_devices():
    result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = result.stdout.strip().split("\n")[1:]  # bỏ dòng đầu "List of devices attached"
    device_ids = [line.split()[0] for line in lines if "device" in line]
    return device_ids



