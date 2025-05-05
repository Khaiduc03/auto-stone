SAVE_IMAGE = True  # Có lưu ảnh annotate không
TEMPLATE_PATH = "./growstone/quiz/faces/slim-fninja2.png"
DEVICE_ID = None  # ID thiết bị ADB nếu có nhiều thiết bị
GRASS_ROI = (80, 960, 1000, 290)  # Vùng quan tâm (x0, y0, w, h)
SEARCH_USER_ROI = (400,1265,250, 110)
THRESHOLD = 0.6  # Ngưỡng matchTemplate
HIST_THRESHOLD = 0.01  # Ngưỡng histogram correlation
SCALE_MIN = 1.0  # Hệ số scale nhỏ nhất
SCALE_MAX = 10.0  # Hệ số scale lớn nhất
FINE_STEPS = 10  # Số bước lọc chi tiết

COARSE_STEPS = 10 # Số bước lọc thô
OUTPUT_PATH = "debug.png"  # Đường dẫn lưu ảnh
