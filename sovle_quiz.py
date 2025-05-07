import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional
from functools import lru_cache
from detect_utils import detect_template
import random
import math
import time  # Thư viện đo thời gian
import uiautomator2 as u2
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
CAPTCHA_Y
)

from character_utils import detect_characters_group_bbox
def find_search_user(img:np.ndarray ):
    list_search_user = [
        "./growstone/quiz/searchs/blue1.png",
        "./growstone/quiz/searchs/blue2.png",
        "./growstone/quiz/searchs/boy1.png",
        "./growstone/quiz/searchs/boy2.png",
        "./growstone/quiz/searchs/boy3.png",
        "./growstone/quiz/searchs/boy4.png",
        "./growstone/quiz/searchs/doge1.png",
        "./growstone/quiz/searchs/doge2.png",
        "./growstone/quiz/searchs/girl1.png",
        "./growstone/quiz/searchs/girl2.png",
        "./growstone/quiz/searchs/kakasi1.png",
        "./growstone/quiz/searchs/kakasi2.png",
        "./growstone/quiz/searchs/ninja-girl1.png",
        "./growstone/quiz/searchs/ninja-girl2.png",
        "./growstone/quiz/searchs/search-wrgirl1.png",
        "./growstone/quiz/searchs/search-wrgirl2.png",
    ]
    x, y, w, h = SEARCH_USER_ROI
    for idx ,user in enumerate(list_search_user):
        try:
            annotated, result = detect_template(img, user, SEARCH_USER_ROI, 0.7,-1,0.5,SCALE_MAX,20,25,None, False )
            if(result):
                #print(f'user find is index {idx}: ' , user)
                # x1, y1 = result["top_left"]
                # x2, y2 = result["bottom_right"]
               
                
                # crop = img[y:y+h, x:x+w]
                # crop2 = img[y1:y2, x1:x2]
                # cv2.imwrite("cropped.png", crop)
                # cv2.imwrite("cropped2.png", crop2)
                return idx
                #
        except ValueError as e:
            msg, x1, y1, x2, y2 = e.args

            # print(f"[{idx}] Phát hiện thất bại: {msg!r} – user={user}")
            # print(f"  → Coordinates from exception: x1={x1}, y1={y1}, x2={x2}, y2={y2}\n")
            
            # crop = img[y:y+h, x:x+w]
            # crop2 = img[y1:y2, x1:x2]
            # cv2.imwrite(f"./debug_out/cropped{idx}.png", crop)
            # cv2.imwrite(f"./debug_out2/c2ropped{idx}.png", crop2)



def get_search_user(img:np.ndarray):
    idx = find_search_user(img)
    match idx:
        case 0 | 1:
            print("Blue")
            return "./growstone/quiz/faces/slim-blue2.png"
        case 2 | 3 | 4 | 5:
            return "./growstone/quiz/faces/slim-boy2.png"
        case 6 | 7:
            print('Doge')
            return "./growstone/quiz/faces/slim-doge1.png"
        case 8 | 9:
            print('Girl')
            return "./growstone/quiz/faces/slim-bhgirl3.png"
        case 10 | 11:
            print('Kakasi')
            return "./growstone/quiz/faces/slim-ninja2.png"
        case 12 | 13:
            print('Ninja girl')
            return "./growstone/quiz/faces/slim-fninja1.png"
        case 14 | 15:
            print('Wgirl')
            return "./growstone/quiz/faces/slim-wrgirl1.png"
        case _:
            print('Not found')
            
            cv2.imwrite(f"./debug_out/error{time.time()}.png", img)
            # cv2.imwrite(f"./debug_out2/c2ropped{idx}.png", img)
    return idx    



def sovle_capcha(img:np.ndarray):
    slim_image = get_search_user(img)

    x1_ug, y1_ug,x2_ug, y2_ug = detect_characters_group_bbox(img)
    crop2 = img[y1_ug:y2_ug, x1_ug:x2_ug]
    cv2.imwrite("cropped3.png", crop2)
    divided_by_four = round((x2_ug - x1_ug)/ 4,1)
    print('divided_by_four', divided_by_four)
    print(f"Vùng phát hiện x1_1: {x1_ug}, x2_2: {x2_ug}, khai: {x2_ug - x1_ug}")
    try:
        annotated, result = detect_template(
            img,
            slim_image,
            GRASS_ROI,
        )
        print("result", result)
    except ValueError as e:
        # Xử lý lỗi không tìm được match
        print(f"Phát hiện thất bại: {e}",)
    x1, y1 = result["top_left"] 
    # print("x1", x1)
    count =0
    for i in range(5):
        if divided_by_four*count <= x1<= divided_by_four * (count +1):
            print("divided_by_four", divided_by_four*count)
            print("x1: ",x1)
            print("divided_by_four+divided_by_four", divided_by_four * (count +1))
            break
        print("divided_by_four1", divided_by_four*count)
        print("x11: ",x1)
        print("divided_by_four+divided_by_four1", divided_by_four * (count +1))
        print()
        count += 1                # tăng đếm lên 1
        
    cv2.imwrite(OUTPUT_PATH, annotated)
    print(f"✅ Đã lưu ảnh → {OUTPUT_PATH}")
    print('count', count)
    
def detech_slim_user(img: np.ndarray, roi: tuple[int, int, int, int]):
    list_slim_user = [
        "./growstone/quiz/faces/slim-blue2.png",
        "./growstone/quiz/faces/slim-boy2.png",
        "./growstone/quiz/faces/slim-doge1.png",
        "./growstone/quiz/faces/slim-bhgirl3.png",
        "./growstone/quiz/faces/slim-ninja2.png",
        "./growstone/quiz/faces/slim-fninja1.png",
        "./growstone/quiz/faces/slim-wrgirl1.png"
    ]

    matched_users = []  # Biến để lưu kết quả (x1, idx)

    for idx, user in enumerate(list_slim_user):
        try:
            annotated, result = detect_template(img, user, roi, 0.65, -1, 0.5, SCALE_MAX, 20, 20, None, False)
            if result:
                x1, y1 = result["top_left"]
                print(f'user find is index {idx}- x1: {x1} - match_score: {result['match_score']} - hist_corr: {result['hist_corr']} - user:{user}' )
                # cv2.imwrite(f'./debug_list_slim/image{idx}.png', annotated)
                # print(f"✅ Đã lưu ảnh → ./debug_list_slim/image{idx}.png")
                # print()
               
                matched_users.append((x1, user))  # Lưu lại khi tìm được
        except ValueError as e:
            msg, x1, y1, x2, y2 = e.args
            print(f"[{idx}] Phát hiện thất bại: {msg!r} – user={user}")
            print(f"  → Coordinates from exception: x1={x1}, y1={y1}, x2={x2}, y2={y2}\n")
            x, y, w, h = roi
            # crop = img[y:y+h, x:x+w]
            # crop2 = img[y1:y2, x1:x2]
            # # cv2.imwrite(f"./debug_out/cropped{idx}.png", crop)
            # cv2.imwrite(f"./debug_out2/cropped{idx}.png", crop2)
            print()
    matched_users.sort()
    return matched_users

      
def find_user_index_by_path(matched_users: list[tuple[int, str]], x: str) -> int | None:
    for idx, (_, user) in enumerate(matched_users):
        if user == x:
            return min(max(idx + 1, 1), 4)
    return None


def sovle_capchav2(img:np.ndarray):
    slim_image = get_search_user(img)

    # x1_ug, y1_ug,x2_ug, y2_ug,w, h  = detect_characters_group_bbox(img)
    # crop = img[y1_ug:y1_ug+h, x1_ug:x1_ug+w]
    # cv2.imwrite("cropped3.png", crop)
    # roi = (x1_ug, y1_ug, x2_ug-x1_ug, y2_ug-y1_ug)
    matched_users = detech_slim_user(img, GRASS_ROI)
    print("matched_users", matched_users)
    if  matched_users.__len__() != 4:
        #how to throw error
        cv2.imwrite(f"./error/error{time.time()}.png", img)
        print("❌ Không tìm thấy đủ 4 người")
        return
    
        
    idx = find_user_index_by_path(matched_users, slim_image)
    return idx


def uiauto_tap(x, y, radius=15, device_ip="127.0.0.1"):
    # Random điểm trong bán kính
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.uniform(0, 1))
    dx = int(r * math.cos(angle))
    dy = int(r * math.sin(angle))

    rx, ry = x + dx, y + dy

    # Delay nhỏ để giả lập thao tác người
    time.sleep(random.uniform(0.2, 0.3))

    # Kết nối và tap
    d = u2.connect(device_ip)
    d.click(rx, ry)

def tap_capcha(device_id=None, full_img:np.ndarray = None):
    idx = sovle_capchav2(full_img)
    print("Người dùng tìm thấy là: ", idx)
    match idx:
        case 1:
            uiauto_tap(CAPTCHA_1, CAPTCHA_Y, 10, device_ip=device_id)
        case 2:
            uiauto_tap(CAPTCHA_2, CAPTCHA_Y, 10, device_ip=device_id)
        case 3:
            uiauto_tap(CAPTCHA_3, CAPTCHA_Y, 10, device_ip=device_id)
        case 4:
            uiauto_tap(CAPTCHA_4, CAPTCHA_Y, 10, device_ip=device_id)

def is_captcha_present(image):
    try:
        _, info = detect_template(image, CAPTCHA_TEMPLATE, CAPTCHA_ROI, 0.5, -1, 0.5, SCALE_MAX, 10, 10, None, False)
        print(f"[CAPTCHA] Đã phát hiện tại {info['top_left']}, score: {info['match_score']:.2f}")
        return True
    except Exception:
        return False

def main_resolve_quiz(device_id=None, screen:np.ndarray = None):
    try:
        if is_captcha_present(screen):
            print(f"[{device_id}] ✓ Đã phát hiện CAPTCHA")
            tap_capcha(device_id, full_img=screen)
        else:
            print(f"[{device_id}] ✓ Không phát hiện CAPTCHA")
    except Exception as e:
        print(f"[{device_id}] Lỗi: {e}")