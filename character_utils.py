

import cv2
import numpy as np



def detect_characters_group_bbox(
    img: np.ndarray,
    grass_roi: tuple = (80, 960, 1000, 290),
    closing_kernel: tuple[int,int] = (50, 5),
    opening_kernel: tuple[int,int] = (5, 5)
) -> tuple[int,int,int,int]:
    """
    Tìm bounding box chung của nhóm character trên ROI cỏ.
    Trả về (x1, y1, x2, y2) tuyệt đối trên ảnh gốc.
    """

    x_off, y_off, w_off, h_off = grass_roi
    # 1) Crop ROI
    grass = img[y_off:y_off+h_off, x_off:x_off+w_off]

    # 2) Gray + Otsu tách vùng tối (là character)
    gray = cv2.cvtColor(grass, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )

    # 3) Closing ngang để nối các nhân vật lại thành 1 blob
    k_close = cv2.getStructuringElement(cv2.MORPH_RECT, closing_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_close)

    # 4) Opening nhỏ để loại bỏ noise lẻ tẻ
    k_open = cv2.getStructuringElement(cv2.MORPH_RECT, opening_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k_open)

    # 5) Connected Components: tìm blob lớn nhất (bỏ qua label 0 là background)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n_labels <= 1:
        raise RuntimeError("Không tìm thấy blob nào ngoài background!")

    # stats: mỗi hàng [left, top, width, height, area]
    # tìm nhãn có diện tích lớn nhất, bắt đầu từ 1
    areas = stats[1:, cv2.CC_STAT_AREA]
    best = 1 + int(np.argmax(areas))
    x, y = stats[best, cv2.CC_STAT_LEFT], stats[best, cv2.CC_STAT_TOP]
    w, h = stats[best, cv2.CC_STAT_WIDTH], stats[best, cv2.CC_STAT_HEIGHT]

    # 6) Đổi thành toạ độ ảnh gốc
    x1, y1 = x_off + x, y_off + y
    x2, y2 = x_off + x + w, y_off + y + h

    return x1, y1, x2, y2











