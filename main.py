import cv2  # Thư viện OpenCV dùng để xử lý ảnh
import numpy as np  # Thư viện numpy hỗ trợ thao tác mảng
import time  # Thư viện đo thời gian
import random
import math
#from typing import Tuple, Dict, Any, Optional  # Khai báo kiểu dữ liệu
from character_utils import detect_characters_group_bbox
from detect_utils import detect_template
from sovle_quiz import find_search_user ,get_search_user,sovle_capcha,sovle_capchav2
from constants import (
DEVICE_ID,
TEMPLATE_PATH,
GRASS_ROI,
SAVE_IMAGE,
OUTPUT_PATH
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


if __name__ == "__main__":
    import subprocess
    import sys
    start_time = time.time()  # Bắt đầu đo tổng thời gian

    full_img = adb_screencap()
    for i in range(5):
        sovle_capchav2(full_img)


    # x1_1, y1_1, x2_1, y2_1 = detect_characters_group_bbox(full_img)

    # divided_by_four = round((x2_1 - x1_1)/ 4,1)
    


    # try:
    #     annotated, result = detect_template(
    #         full_img,
    #         TEMPLATE_PATH,
    #         GRASS_ROI,
    #     )
    # except ValueError as e:
    #     # Xử lý lỗi không tìm được match
    #     print(f"Phát hiện thất bại: {e}", file=sys.stderr)
    #     sys.exit(1)



    # x1, y1 = result["top_left"]
    # x2, y2 = result["bottom_right"]
    # # print("divided_by_four ",divided_by_four)
    # # print(f"Vùng phát hiện x1_1: {x1_1}, x2_2: {x2_1}")
    # # print(f"Vùng phát hiện x1: {x1}, x2: {x2}")


    # count =0
    # for i in range(5):
    #     if divided_by_four*count <= x1<= divided_by_four * (count +1):
    #         # print("divided_by_four", divided_by_four*count)
    #         # print("x1: ",x1)
    #         # print("divided_by_four+divided_by_four", divided_by_four * (count +1))
    #         break
    #     count += 1                # tăng đếm lên 1
        

    # print('count', count)


    # #Lưu ảnh nếu cần
    # if SAVE_IMAGE and annotated is not None:
    #     cv2.imwrite(OUTPUT_PATH, annotated)
    #     print(f"✅ Đã lưu ảnh → {OUTPUT_PATH}")


    # # In tổng thời gian
    # print(f"Tổng thời gian: {time.time() - start_time:.2f} giây")
