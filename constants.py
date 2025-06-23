import sys
import os

def resource_path(rel_path: str) -> str:
    """
    Trả về đường dẫn tuyệt đối tới tài nguyên, 
    dùng cho cả khi chạy code gốc và khi đã bundle bằng PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller onefile sẽ giải nén vào _MEIPASS
        base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    else:
        # bình thường: chạy script gốc
        base = os.path.abspath(".")
    return os.path.join(base, rel_path)

SAVE_IMAGE = False  # Có lưu ảnh annotate không
TEMPLATE_PATH = resource_path("growstone/quiz/faces/slim-fninja2.png")
DEVICE_ID = None  # ID thiết bị ADB nếu có nhiều thiết bị
GRASS_ROI = (42, 358, 455, 137)  # Vùng quan tâm (x0, y0, w, h)
CAPTCHA_ROI = (80, 215, 400, 60)  # Vùng quan tâm cho captcha
SEARCH_USER_ROI = (220,505,130, 95)
RUBY_ROI = (10, 525, 290, 250)  # Vùng quan tâm cho ruby
DUNGEON_ROI = (10,385, 62, 215)  # Vùng quan tâm cho dungeon
STONE_ROI= (34, 1780, 910, 460)  # Vùng quan tâm cho stone, sẽ được cập nhật sau khi tìm thấy stone
THRESHOLD = 0.6  # Ngưỡng matchTemplate
HIST_THRESHOLD = 0.01  # Ngưỡng histogram correlation
SCALE_MIN = 1.0  # Hệ số scale nhỏ nhất
SCALE_MAX = 10.0  # Hệ số scale lớn nhất
FINE_STEPS = 20  # Số bước lọc chi tiết

COARSE_STEPS = 20 # Số bước lọc thôz
OUTPUT_PATH = "debug.png"  # Đường dẫn lưu ảnh
CAPTCHA_TEMPLATE = resource_path("growstone/quiz/surprise-quiz.png")
RUBY_PNG       = resource_path("growstone/quiz/ruby_box2.png")
DUNGEON_PNG    = resource_path("growstone/quiz/dungeon.png")
CAPTCHA_1 =95
CAPTCHA_2 =209
CAPTCHA_3 =324
CAPTCHA_4 =445
CAPTCHA_Y = 704





SEARCH_USER_IMAGES = [
    resource_path('growstone/quiz/searchs/blue1.png'),
    resource_path('growstone/quiz/searchs/blue2.png'),
    resource_path('growstone/quiz/searchs/boy1.png'),
    resource_path('growstone/quiz/searchs/boy2.png'),
    resource_path('growstone/quiz/searchs/boy3.png'),
    resource_path('growstone/quiz/searchs/boy4.png'),
    resource_path('growstone/quiz/searchs/doge1.png'),
    resource_path('growstone/quiz/searchs/doge2.png'),
    resource_path('growstone/quiz/searchs/girl1.png'),
    resource_path('growstone/quiz/searchs/girl2.png'),
    resource_path('growstone/quiz/searchs/kakasi1.png'),
    resource_path('growstone/quiz/searchs/kakasi2.png'),
    resource_path('growstone/quiz/searchs/ninja-girl1.png'),
    resource_path('growstone/quiz/searchs/ninja-girl2.png'),
    resource_path('growstone/quiz/searchs/search-wrgirl1.png'),
    resource_path('growstone/quiz/searchs/search-wrgirl2.png'),
]

# Đường dẫn faces cho từng nhóm user
SLIM_FACES = {
    'blue': resource_path('growstone/quiz/faces/slim-blue2.png'),
    'boy': resource_path('growstone/quiz/faces/slim-boy2.png'),
    'doge': resource_path('growstone/quiz/faces/slim-doge1.png'),
    'girl': resource_path('growstone/quiz/faces/slim-bhgirl3.png'),
    'kakasi': resource_path('growstone/quiz/faces/slim-ninja2.png'),
    'ninja': resource_path('growstone/quiz/faces/slim-fninja1.png'),
    'wgirl': resource_path('growstone/quiz/faces/slim-wrgirl1.png'),
}