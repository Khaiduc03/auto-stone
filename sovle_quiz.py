import cv2
import numpy as np
from typing import Tuple, List, Optional
import random
import math
import time  # Thư viện đo thời gian
import uiautomator2 as u2
from uiautomator2 import Device
from detect_utils import detect_template
from character_utils import detect_characters_group_bbox
from constants import (
    SCALE_MAX,
    SEARCH_USER_ROI,
    GRASS_ROI,
    OUTPUT_PATH,
    CAPTCHA_TEMPLATE,
    CAPTCHA_ROI,
    CAPTCHA_1,
    CAPTCHA_2,
    CAPTCHA_3,
    CAPTCHA_4,
    CAPTCHA_Y,
    SEARCH_USER_IMAGES,
    SLIM_FACES,
)

def find_search_user(img: np.ndarray) -> Optional[int]:
    """
    Quét qua tất cả ảnh SEARCH_USER_IMAGES, trả về index nếu tìm thấy.
    """
    for idx, template_path in enumerate(SEARCH_USER_IMAGES):
        try:
            annotated, result = detect_template(
                img,
                template_path,
                SEARCH_USER_ROI,
                0.7, -1, 0.5,
                SCALE_MAX, 20, 25,
                None, False
            )
            if result:
                return idx
        except ValueError:
            continue
    return None


def get_search_user(img: np.ndarray) -> str:
    """
    Dựa vào index trả về từ find_search_user, chọn face tương ứng.
    """
    idx = find_search_user(img)
    if idx is None:
        print('Not found')
        cv2.imwrite(f"./debug_out/error{time.time()}.png", img)
        return ''

    # phân nhóm theo index
    if idx < 2:
        key = 'blue'
    elif idx < 6:
        key = 'boy'
    elif idx < 8:
        key = 'doge'
    elif idx < 10:
        key = 'girl'
    elif idx < 12:
        key = 'kakasi'
    elif idx < 14:
        key = 'ninja'
    else:
        key = 'wgirl'

    print(key.capitalize())
    return SLIM_FACES[key]


def solve_capcha(img: np.ndarray) -> None:
    slim_image = get_search_user(img)
    if not slim_image:
        return

    x1_ug, y1_ug, x2_ug, y2_ug = detect_characters_group_bbox(img)
    crop2 = img[y1_ug:y2_ug, x1_ug:x2_ug]
    cv2.imwrite("cropped3.png", crop2)

    divided_by_four = round((x2_ug - x1_ug) / 4, 1)
    print('divided_by_four', divided_by_four)

    try:
        annotated, result = detect_template(
            img,
            slim_image,
            GRASS_ROI,
        )
        print('result', result)
    except ValueError as e:
        print(f"Phát hiện thất bại: {e}")
        return

    x1, _ = result["top_left"]
    count = 0
    for i in range(5):
        if divided_by_four * count <= x1 <= divided_by_four * (count + 1):
            break
        count += 1

    cv2.imwrite(OUTPUT_PATH, annotated)
    print(f"✅ Đã lưu ảnh → {OUTPUT_PATH}")
    print('count', count)


def detect_slim_user(img: np.ndarray, roi: Tuple[int, int, int, int]) -> List[tuple[int, str]]:
    """
    Tìm tất cả user trong ROI, trả về list (x1, path).
    """
    matched_users: List[tuple[int, str]] = []
    for idx, face_path in enumerate(SLIM_FACES.values()):
        try:
            annotated, result = detect_template(
                img,
                face_path,
                roi,
                0.60, -1, 0.5,
                SCALE_MAX, 20, 20,
                None, False
            )
            if result:
                x1, _ = result['top_left']
                matched_users.append((x1, face_path))
        except ValueError as e:
            continue
    matched_users.sort(key=lambda t: t[0])
    return matched_users


def find_user_index_by_path(matched_users: List[tuple[int, str]], path: str) -> Optional[int]:
    for idx, (_, user_path) in enumerate(matched_users):
        if user_path == path:
            return min(max(idx + 1, 1), 4)
    return None


def solve_capchav2(img: np.ndarray) -> Optional[int]:
    slim_image = get_search_user(img)
    if not slim_image:
        return None

    matched = detect_slim_user(img, GRASS_ROI)
    print('matched_users', matched)
    if len(matched) != 4:
        print('❌ Không tìm thấy đủ 4 người')
        return None

    return find_user_index_by_path(matched, slim_image)


def uiauto_tap(x: int, y: int, radius: int = 15, device_ip: str = "127.0.0.1") -> None:
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.uniform(0, 1))
    dx = int(r * math.cos(angle))
    dy = int(r * math.sin(angle))
    rx, ry = x + dx, y + dy
    time.sleep(random.uniform(0.2, 0.3))
    u2.connect(device_ip).click(rx, ry)

def uiauto_tap2(x: int, y: int, radius: int = 15, u2: Device = None) -> None:
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.uniform(0, 1))
    dx = int(r * math.cos(angle))
    dy = int(r * math.sin(angle))
    rx, ry = x + dx, y + dy
    time.sleep(random.uniform(0.2, 0.3))
    u2.click(rx, ry)


def tap_capcha(device_id: Optional[str] = None, full_img: np.ndarray = None, u2: Device = None) -> None:
    idx = solve_capchav2(full_img)
    print('Người dùng tìm thấy là:', idx)
    match idx:
        case 1:
            uiauto_tap2(CAPTCHA_1, CAPTCHA_Y, 10, u2)
        case 2:
            uiauto_tap2(CAPTCHA_2, CAPTCHA_Y, 10, u2)
        case 3:
            uiauto_tap2(CAPTCHA_3, CAPTCHA_Y, 10,u2)
        case 4:
            uiauto_tap2(CAPTCHA_4, CAPTCHA_Y, 10, u2)


def is_captcha_present(image: np.ndarray) -> bool:
    try:
        _, info = detect_template(
            image,
            CAPTCHA_TEMPLATE,
            CAPTCHA_ROI,
            0.5, -1, 0.5,
            SCALE_MAX, 10, 10,
            None, False
        )
        print(f"[CAPTCHA] Đã phát hiện tại {info['top_left']}, score: {info['match_score']:.2f}")
        return True
    except Exception:
        return False


def main_resolve_quiz(device_id: Optional[str] = None, screen: np.ndarray = None, name: Optional[str] = None, u2: Device= None) -> None:
    try:
        if is_captcha_present(screen):
            print(f"[{device_id}] ✓ Đã phát hiện CAPTCHA")
            tap_capcha(device_id, full_img=screen, u2=u2)
        else:
            print(f"[{device_id}-{name}] ✓ Không phát hiện CAPTCHA")
    except Exception as e:
        print(f"[{device_id}] Lỗi: {e}")