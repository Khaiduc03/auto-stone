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

def adb_screencap_adb(device_id: str | None = None) -> np.ndarray | None:
    """
    Chụp màn hình qua ADB shell (exec-out screencap -p) thuần túy,
    không dùng uiautomator2, trả về OpenCV BGR ndarray.
    """
    cmd = ["adb"]
    if device_id:
        cmd += ["-s", device_id]
    cmd += ["exec-out", "screencap -p"]

    try:
        data = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode().strip() if e.stderr else str(e)
        print(f"ADB screencap error: {err}", file=sys.stderr)
        return None
    except OSError as e:
        print(f"Lỗi khi chạy adb: {e}", file=sys.stderr)
        return None

    if not data:
        print("Không có dữ liệu ảnh từ adb.", file=sys.stderr)
        return None

    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        print("Không decode được dữ liệu ảnh từ adb.", file=sys.stderr)
    return img

def get_connected_devices():
    result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = result.stdout.strip().split("\n")[1:]  # bỏ dòng đầu "List of devices attached"
    device_ids = [line.split()[0] for line in lines if "device" in line]
    return device_ids



