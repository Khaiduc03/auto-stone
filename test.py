import sys
import subprocess
from datetime import datetime

import cv2
import numpy as np
import uiautomator2 as u2

from constants import RUBY_ROI   # (x0, y0, w0, h0) gốc trên 540×960

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

def map_roi(orig_roi, orig_size, target_size):
    x0, y0, w0, h0 = orig_roi
    W0, H0         = orig_size
    W1, H1         = target_size
    return (
        int(x0 * W1 / W0),
        int(y0 * H1 / H0),
        int(w0 * W1 / W0),
        int(h0 * H1 / H0),
    )

def testScaleRoi():
    # 1) chụp màn hình
    screen = adb_screencap_adb()
    if screen is None:
        print("Không chụp được màn hình, thoát.")
        return

    # 2) tính ROI
    height, width  = screen.shape[:2]
    orig_size      = (540, 960)     # size lúc đo RUBY_ROI
    target_size    = (width, height)

    x, y, rw, rh   = map_roi(RUBY_ROI, orig_size, target_size)
    print(f"Computed ROI on this device: {(x, y, rw, rh)}")

    # 3) cắt ảnh
    roi_crop = screen[y : y + rh, x : x + rw]

    # 4) lưu xuống ổ
 
    filename = f"ruby_roi.png"
    if cv2.imwrite(filename, roi_crop):
        print(f"Saved cropped ROI to {filename}")
    else:
        print("Lỗi khi lưu ảnh.", file=sys.stderr)

if __name__ == "__main__":
    testScaleRoi()
