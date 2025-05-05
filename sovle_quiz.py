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
        "./growstone/quiz/faces/search-bhgirl1.png",
        "./growstone/quiz/faces/search-blue1.png",
        "./growstone/quiz/faces/search-boy.png",
        "./growstone/quiz/faces/search-boy2.png",
        "./growstone/quiz/faces/search-doge1.png",
        "./growstone/quiz/faces/search-fninja1.png",
        "./growstone/quiz/faces/search-ninja1.png",
        "./growstone/quiz/faces/search-wrgirl1.png",
        "./growstone/quiz/faces/search-wrgirl2.png",
        "./growstone/quiz/faces/search-wrgirl.png",
    ]
    x, y, w, h = SEARCH_USER_ROI
    for idx ,user in enumerate(list_search_user):
        try:
            result = detect_template(img, user, SEARCH_USER_ROI, THRESHOLD,0.00,0.5,SCALE_MAX,COARSE_STEPS,FINE_STEPS,None, False )
            if(result):
                print('user find is: ' , user)
               
                crop = img[y:y+h, x:x+w]
                cv2.imwrite("cropped.jpg", crop)
                break
        except ValueError as e:
            print(f"Phát hiện thất bại: {e} - {user} - {idx}")
            # crop = img[y:y+h, x:x+w]
            # cv2.imwrite(f"./debug_out/cropped{idx}.jpg", crop)



    
    