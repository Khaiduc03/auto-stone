import cv2  # Thư viện OpenCV dùng để xử lý ảnh
import numpy as np  # Thư viện numpy hỗ trợ thao tác mảng
import time  # Thư viện đo thời gian
from typing import Tuple, Dict, Any, Optional  # Khai báo kiểu dữ liệu
from character_utils import detect_characters_group_bbox

def multi_scale_template_match(
    gray_roi: np.ndarray,
    tpl: np.ndarray,
    scale_min: float = 1.0,
    scale_max: float = 10.0,
    scale_steps: int = 20
) -> Dict[str, Any]:
    """
    Thực hiện tìm template ở nhiều tỉ lệ (scale) trong vùng ảnh xám (gray_roi).
    Trả về dict chứa thông tin kết quả tốt nhất: điểm số, vị trí, kích thước, scale.
    """
    h0, w0 = tpl.shape  # Kích thước gốc của template: chiều cao và rộng
    # Khởi tạo kết quả tốt nhất ban đầu
    best = {"val": -1.0, "loc": None, "wh": (w0, h0), "scale": 1.0}
    # Duyệt qua các giá trị scale từ nhỏ đến lớn
    for s in np.linspace(scale_min, scale_max, scale_steps):
        w, h = int(w0 * s), int(h0 * s)  # Tính kích thước template sau khi scale
        # Bỏ qua template quá nhỏ hoặc quá lớn so với ROI
        if w < 10 or h < 10 or w > gray_roi.shape[1] or h > gray_roi.shape[0]:
            continue
        # Thay đổi kích thước template theo scale hiện tại
        tpl_rs = cv2.resize(tpl, (w, h), interpolation=cv2.INTER_AREA)
        # So khớp template: trả về ma trận kết quả
        res = cv2.matchTemplate(gray_roi, tpl_rs, cv2.TM_CCOEFF_NORMED)
        # Lấy giá trị max và vị trí tương ứng
        _, mx, _, pt = cv2.minMaxLoc(res)
        # Cập nhật kết quả tốt nhất nếu điểm cao hơn
        if mx > best["val"]:
            best.update(val=mx, loc=pt, wh=(w, h), scale=s)
    return best  # Trả về kết quả tốt nhất


def detect_template(
    image: np.ndarray,
    template_path: str,
    roi: Tuple[int, int, int, int],  # (x0, y0, width, height)
    threshold: float = 0.5,
    hist_threshold: float = 0.0,
    scale_min: float = 1.0,
    scale_max: float = 10.0,
    scale_steps: int = 20,
    annotate: bool = True
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    """
    Phát hiện template trong ảnh nhập vào (image) tại vùng ROI.
    Nếu annotate=True, trả về ảnh có vẽ khung; ngược lại chỉ trả về info.
    """
    # Đọc template dưới dạng ảnh xám
    tpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        # Không tìm thấy file template
        raise ValueError(f"Không tìm thấy template: {template_path}")

    # Giải nén tọa độ ROI
    x0, y0, w, h = roi
    # Chuyển ảnh gốc sang xám để match
    gray_full = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Cắt vùng ROI từ ảnh xám
    gray_roi = gray_full[y0:y0+h, x0:x0+w]

    # Đo thời gian thực thi tìm kiếm
    start_time = time.time()
    best = multi_scale_template_match(
        gray_roi, tpl, scale_min, scale_max, scale_steps
    )
    match_time = time.time() - start_time  # Thời gian hoàn thành

    # Kiểm tra ngưỡng điểm match
    if best["val"] < threshold:
        raise ValueError(
            f"Không có kết quả match đủ {threshold}, điểm cao nhất={best['val']:.2f}"
        )

    # Lấy vị trí và kích thước của vùng match
    bx, by = best["loc"]  # Tọa độ top-left trong ROI
    bw, bh = best["wh"]
    # Cắt miếng ảnh match để kiểm tra histogram
    patch = gray_roi[by:by+bh, bx:bx+bw]
    # Tính histogram của template và patch
    hist_tpl = cv2.calcHist([tpl], [0], None, [256], [0, 256])
    hist_patch = cv2.calcHist([patch], [0], None, [256], [0, 256])
    cv2.normalize(hist_tpl, hist_tpl)  # Chuẩn hóa histogram
    cv2.normalize(hist_patch, hist_patch)
    hist_corr = cv2.compareHist(hist_tpl, hist_patch, cv2.HISTCMP_CORREL)
    # Kiểm tra ngưỡng histogram
    if hist_corr < hist_threshold:
        raise ValueError(
            f"Histogram không đủ tin cậy: {hist_corr:.2f} < {hist_threshold}"
        )

    # Chuẩn bị dict kết quả
    info = {
        "roi": roi,
        "top_left": (x0 + bx, y0 + by),  # Chuyển sang toạ độ ảnh gốc
        "bottom_right": (x0 + bx + bw, y0 + by + bh),
        "match_score": best["val"],
        "hist_corr": hist_corr,
        "scale": best["scale"],
        "template_size": best["wh"],
        "match_time": match_time,
    }

    # Nếu cần annotate, vẽ khung và ghi thông tin
    if annotate:
        annotated = image.copy()
        cv2.rectangle(
            annotated,
            info["top_left"],
            info["bottom_right"],
            (0, 255, 0),
            3
        )
        note = f"{best['val']:.2f}@x{best['scale']:.2f}|h={hist_corr:.2f}"
        cv2.putText(
            annotated,
            note,
            (info["top_left"][0], info["top_left"][1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        return annotated, info  # Trả về ảnh đã annotate và kết quả

    # Nếu không annotate, trả về None cho ảnh
    return None, info




if __name__ == "__main__":
    import subprocess
    import sys
    start_time = time.time()  # Bắt đầu đo tổng thời gian

    # Cấu hình tham số
    SAVE_IMAGE = True  # Có lưu ảnh annotate không
    TEMPLATE_PATH = "./growstone/quiz/faces/slim-bhgirl1.png"
    DEVICE_ID = None  # ID thiết bị ADB nếu có nhiều thiết bị
    GRASS_ROI = (80, 960, 1000, 290)  # Vùng quan tâm (x0, y0, w, h)
    THRESHOLD = 0.5  # Ngưỡng matchTemplate
    HIST_THRESHOLD = 0.0  # Ngưỡng histogram correlation
    SCALE_MIN = 1.0  # Hệ số scale nhỏ nhất
    SCALE_MAX = 10.0  # Hệ số scale lớn nhất
    SCALE_STEPS = 20  # Số bước scale
    OUTPUT_PATH = "debug.png"  # Đường dẫn lưu ảnh

    def adb_screencap(device_id=None):
        # Chụp màn hình qua ADB và giải mã thành ảnh OpenCV
        cmd = ["adb"] + (
            ["-s", device_id] if device_id else []
        ) + ["exec-out", "screencap", "-p"]
        raw = subprocess.check_output(cmd)
        arr = np.frombuffer(raw, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            print("Lỗi giải mã ảnh ADB", file=sys.stderr)
            sys.exit(1)
        return img

    full_img = adb_screencap(DEVICE_ID)  # Chụp screenshot
    x1_1, y1_1, x2_1, y2_1 = detect_characters_group_bbox(full_img)
    # Khoanh đỏ
    #cv2.rectangle(full_img, (x1_1, y1_1), (x2_1, y2_1), (0,0,255), 2)
    #cv2.imwrite('boxed_group_precise.png', full_img)
    #print(f"Box: top-left=({x1_1},{y1_1}), bottom-right=({x2_1},{y2_1})")
    divided_by_four = round((x2_1 - x1_1)/ 4,1)
    print('divided_by_four', divided_by_four)
    


    try:
        annotated, result = detect_template(
            full_img,
            TEMPLATE_PATH,
            GRASS_ROI,
            threshold=THRESHOLD,
            hist_threshold=HIST_THRESHOLD,
            scale_min=SCALE_MIN,
            scale_max=SCALE_MAX,
            scale_steps=SCALE_STEPS,
            annotate=SAVE_IMAGE,
        )
    except ValueError as e:
        # Xử lý lỗi không tìm được match
        print(f"Phát hiện thất bại: {e}", file=sys.stderr)
        sys.exit(1)



    x1, y1 = result["top_left"]
    x2, y2 = result["bottom_right"]
    print(f"Vùng phát hiện x1_1: {x1_1}, x2_2: {x2_1}")
    print(f"Vùng phát hiện x1: {x1}, x2: {x2}")
    print(f"hist_corr", result['hist_corr'])
    print
    
    count =0
 

    for i in range(4):
        if divided_by_four*count <= x1<= divided_by_four * (count +1):
            print("x1: ",x1)
            print("divided_by_four", count)
            print("divided_by_four+divided_by_four", count+1)
            break
        count += 1                # tăng đếm lên 1
        


    print('count', count)





    #Lưu ảnh nếu cần
    if SAVE_IMAGE and annotated is not None:
        cv2.imwrite(OUTPUT_PATH, annotated)
        print(f"✅ Đã lưu ảnh → {OUTPUT_PATH}")
    else:
        print("Bỏ qua lưu ảnh (SAVE_IMAGE=False)")

    # In tổng thời gian
    print(f"Tổng thời gian: {time.time() - start_time:.2f} giây")
