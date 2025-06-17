import sys
import subprocess
from datetime import datetime

import cv2
import numpy as np
import uiautomator2 as u2

from constants import CAPTCHA_ROI, RUBY_ROI  # ROI gốc đo trên 540×960

# DPI gốc khi đo ROI
ORIG_DPI = 120

def adb_screencap_adb(device_id: str | None = None) -> np.ndarray | None:
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

def map_roi_by_dpi(orig_roi, dpi_orig, dpi_target):
    """
    orig_roi: (x, y, w, h) đo trên màn orig với density dpi_orig
    dpi_target: density của device đang chạy
    """
    x0, y0, w0, h0 = orig_roi
    scale = dpi_target / dpi_orig
    print(f"Scale: {scale}")
    return (
        int(x0 * scale),
        int(y0 * scale),
        int(w0 * scale),
        int(h0 * scale),
    )

def testScaleRoi(device_id: str | None = None):
    # 1) chụp màn hình
    screen = adb_screencap_adb(device_id)
    if screen is None:
        print("Không chụp được màn hình, thoát.")
        return

    # 2) kết nối uiautomator2 và lấy DPI đúng
    # d = u2.connect_usb(device_id) if device_id else u2.connect()
    # info = d.device_info
    dpi_target =0
    
    # if dpi_target is None:
    #     # fallback: dùng adb shell wm density
    try:
        out = subprocess.check_output(
            ["adb"] + (["-s", device_id] if device_id else []) + ["shell", "wm", "density"]
        ).decode()
        # out format: "Physical density: 480"
        dpi_target = int(out.strip().split()[-1])
    except Exception as e:
        print(f"Không lấy được DPI từ adb: {e}", file=sys.stderr)
        return

    # 3) chọn ROI gốc
    orig_roi = CAPTCHA_ROI     # hoặc CAPTCHA_ROI
    print(f"DPI target: {dpi_target}")
    # 4) map sang px mới
    x, y, rw, rh = map_roi_by_dpi(orig_roi, ORIG_DPI, 360)
    print(f"Mapped ROI using DPI scale: {(x, y, rw, rh)}")

    # 5) cắt và lưu
    roi_crop = screen[y : y + rh, x : x + rw]
 
    filename = f"roi_dpi.png"
    if cv2.imwrite(filename, roi_crop):
        print(f"Saved cropped ROI to {filename}")
    else:
        print("Lỗi khi lưu ảnh.", file=sys.stderr)

if __name__ == "__main__":
    # nếu bạn chỉ có 1 thiết bị hoặc muốn test mặc định thì để None
    testScaleRoi(device_id=None)
