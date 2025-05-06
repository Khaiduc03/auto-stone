SAVE_IMAGE = True  # Có lưu ảnh annotate không
TEMPLATE_PATH = "./growstone/quiz/faces/slim-fninja2.png"
DEVICE_ID = None  # ID thiết bị ADB nếu có nhiều thiết bị
GRASS_ROI = (80, 960, 1000, 290)  # Vùng quan tâm (x0, y0, w, h)
CAPTCHA_ROI = (140, 700, 800, 95)  # Vùng quan tâm cho captcha
SEARCH_USER_ROI = (400,1265,250, 150)
THRESHOLD = 0.6  # Ngưỡng matchTemplate
HIST_THRESHOLD = 0.01  # Ngưỡng histogram correlation
SCALE_MIN = 1.0  # Hệ số scale nhỏ nhất
SCALE_MAX = 10.0  # Hệ số scale lớn nhất
FINE_STEPS = 20  # Số bước lọc chi tiết

COARSE_STEPS = 20 # Số bước lọc thôz
OUTPUT_PATH = "debug.png"  # Đường dẫn lưu ảnh
CAPTCHA_TEMPLATE = "./growstone/quiz/surprise-quiz.png"  # Đường dẫn template captcha
