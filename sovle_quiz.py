import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional
from detect_utils import detect_template
from constants import (
THRESHOLD,HIST_THRESHOLD,
SCALE_MIN,
SCALE_MAX,
COARSE_STEPS,
FINE_STEPS,
SAVE_IMAGE,
SEARCH_USER_ROI
)
def find_search_user(img:np.ndarray ):
    list_search_user = [
        "./growstone/quiz/searchs/blue1.png",
        "./growstone/quiz/searchs/blue2.png",
        "./growstone/quiz/searchs/boy1.png",
        "./growstone/quiz/searchs/boy2.png",
        "./growstone/quiz/searchs/search-boy1.png",
        "./growstone/quiz/searchs/search-boy2.png",
        "./growstone/quiz/searchs/doge1.png",
        "./growstone/quiz/searchs/doge2.png",
        "./growstone/quiz/searchs/girl1.png",
        "./growstone/quiz/searchs/girl2.png",
        "./growstone/quiz/searchs/kakasi1.png",
        "./growstone/quiz/searchs/kakasi2.png",
        "./growstone/quiz/searchs/ninja-girl1.png",
        "./growstone/quiz/searchs/ninja-girl2.png",
        "./growstone/quiz/searchs/wGirl1.png",
        "./growstone/quiz/searchs/wGirl2.png",
    ]
    x, y, w, h = SEARCH_USER_ROI
    for idx ,user in enumerate(list_search_user):
        try:
            annotated, result = detect_template(img, user, SEARCH_USER_ROI, 0.7,0.00,0.5,SCALE_MAX,20,25,None, False )
            if(result):
                print(f'user find is index {idx}: ' , user)
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

            print(f"[{idx}] Phát hiện thất bại: {msg!r} – user={user}")
            print(f"  → Coordinates from exception: x1={x1}, y1={y1}, x2={x2}, y2={y2}\n")
            
            # crop = img[y:y+h, x:x+w]
            # crop2 = img[y1:y2, x1:x2]
            # cv2.imwrite(f"./debug_out/cropped{idx}.png", crop)
            # cv2.imwrite(f"./debug_out2/c2ropped{idx}.png", crop2)



    
    