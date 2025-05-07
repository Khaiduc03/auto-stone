SAVE_IMAGE = False  # Có lưu ảnh annotate không
TEMPLATE_PATH = "./growstone/quiz/faces/slim-fninja2.png"
DEVICE_ID = None  # ID thiết bị ADB nếu có nhiều thiết bị
GRASS_ROI = (42, 358, 455, 137)  # Vùng quan tâm (x0, y0, w, h)
CAPTCHA_ROI = (80, 215, 400, 60)  # Vùng quan tâm cho captcha
SEARCH_USER_ROI = (220,505,130, 95)
RUBY_ROI = (10, 525, 290, 200)  # Vùng quan tâm cho ruby
DUNGEON_ROI = (10,385, 62, 215)  # Vùng quan tâm cho dungeon
THRESHOLD = 0.6  # Ngưỡng matchTemplate
HIST_THRESHOLD = 0.01  # Ngưỡng histogram correlation
SCALE_MIN = 1.0  # Hệ số scale nhỏ nhất
SCALE_MAX = 10.0  # Hệ số scale lớn nhất
FINE_STEPS = 20  # Số bước lọc chi tiết

COARSE_STEPS = 20 # Số bước lọc thôz
OUTPUT_PATH = "debug.png"  # Đường dẫn lưu ảnh
CAPTCHA_TEMPLATE = "./growstone/quiz/surprise-quiz.png"  # Đường dẫn template captcha
RUBY_PNG = "./growstone/quiz/ruby_box2.png"  # Đường dẫn template ruby
DUNGEON_PNG = "./growstone/quiz/dungeon.png"  
CAPTCHA_1 =95
CAPTCHA_2 =209
CAPTCHA_3 =324
CAPTCHA_4 =445
CAPTCHA_Y = 704

