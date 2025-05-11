
import time
from adb_utils import adb_screencap, adb_screencap_adb
from sovle_quiz import uiauto_tap, uiauto_tap2
from detect_utils import detect_template
import cv2
import numpy as np
from constants import (
    SEARCH_USER_ROI,
    RUBY_ROI,
    SCALE_MAX,
    RUBY_PNG,
    DUNGEON_ROI,
    DUNGEON_PNG
)
from uiautomator2 import Device
def auto_click_ruby_box(device_id=None, u2: Device = None ):
    # 1 Chạm vào vị trí ruby get reward
    uiauto_tap2(32, 607,2, u2)
    print("Chạm vào vị trí ruby get reward")
    time.sleep(0.5)
    img = adb_screencap_adb(device_id=device_id)
   
    try:
        _, result = detect_template(img, RUBY_PNG, RUBY_ROI, 0.6,-3,0.5,SCALE_MAX,20,25,None, False )
        x1, y1 = result["top_left"]
        x2, y2 = result["bottom_right"]
            # Tính tâm hình chữ nhật
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        uiauto_tap2(cx, cy, 10, u2)
        uiauto_tap2(90, 525,10, u2)
    except ValueError as e:
        msg, x1, y1, x2, y2 = e.args
        print(f"[{device_id}] Phát hiện thất bại ruby: {msg!r} ")
        print(f"  → Coordinates from exception: x1={x1}, y1={y1}, x2={x2}, y2={y2}\n")
        x, y, w, h = RUBY_ROI
        # crop = img[y:y+h, x:x+w]
        # crop2 = img[y1:y2, x1:x2]
       
        # cv2.imwrite(f"./debug_out2/c2ropped.png", crop2)
        # cv2.imwrite(f"./debug_out2/c1ropped.png", crop)
        uiauto_tap2(90, 525,10, u2)
  

        
        
    # 2. Tìm 

    
def auto_enter_dungeon(device_id=None, img=None, u2=None):
    # 1 Chạm vào vị trí ruby get reward
    
    try:
        _, result = detect_template(img, DUNGEON_PNG, DUNGEON_ROI, 0.5,0.00,0.5,SCALE_MAX,20,25,None, False )
        x1, y1 = result["top_left"]
        x2, y2 = result["bottom_right"]
            # Tính tâm hình chữ nhật
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        uiauto_tap2(cx, cy, 10, u2)
        # uiauto_tap(90, 1656,10, device_id)
    except ValueError as e:
        msg, x1, y1, x2, y2 = e.args
        #print(f"[{device_id}] Phát hiện thất bại: {msg!r} ")
        # print(f"  → Coordinates from exception: x1={x1}, y1={y1}, x2={x2}, y2={y2}\n")
        # # x, y, w, h = RUBY_ROI
        # # crop = img[y:y+h, x:x+w]
        # crop2 = img[y1:y2, x1:x2]
       
        # cv2.imwrite(f"./debug_out2/c2ropped.png", crop2)
        #uiauto_tap(90, 1656,10, device_id)