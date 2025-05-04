import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Dict, Any, Optional


def multi_scale_template_match(
    gray_roi: np.ndarray,
    tpl: np.ndarray,
    scale_min: float = 1.0,
    scale_max: float = 10.0,
    coarse_steps: int = 8,
    fine_steps: int = 20,
    n_workers: int = None,
) -> Dict[str, Any]:
    """
    Tìm template trên vùng ảnh gray_roi theo scale, dùng tìm kiếm 2 giai đoạn và parallel.
    Trả về dict chứa kết quả tốt nhất: score, vị trí, kích thước, scale.
    """
    # Lấy kích thước gốc của template
    h0, w0 = tpl.shape
    # Chuyển về float32 để thao tác nhanh hơn với OpenCV
    gray_f = gray_roi.astype(np.float32)
    tpl_f   = tpl.astype(np.float32)

    # Hàm nội bộ để thực hiện match tại một scale cụ thể
    def match_at_scale(s: float):
        # Tính kích thước mới của template theo scale
        w, h = int(w0 * s), int(h0 * s)
        # Bỏ qua nếu template quá nhỏ hoặc quá lớn so với ROI
        if w < 10 or h < 10 or w > gray_roi.shape[1] or h > gray_roi.shape[0]:
            return None
        # Resize template
        tpl_rs = cv2.resize(tpl_f, (w, h), interpolation=cv2.INTER_AREA)
        # Thực hiện template matching
        res = cv2.matchTemplate(gray_f, tpl_rs, cv2.TM_CCOEFF_NORMED)
        # Lấy giá trị max và vị trí
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        return max_val, max_loc, (w, h), s

    # --- Giai đoạn thô (coarse search) ---
    # Chia đều đoạn scale thành coarse_steps bước
    coarse_scales = np.linspace(scale_min, scale_max, coarse_steps)
    # Khởi tạo kết quả tốt nhất ban đầu
    best = {"val": -1.0, "loc": None, "wh": (w0, h0), "scale": 1.0}

    # Dùng ThreadPoolExecutor để chạy song song các scale
    with ThreadPoolExecutor(max_workers=n_workers) as exe:
        futures = [exe.submit(match_at_scale, s) for s in coarse_scales]
        for f in as_completed(futures):
            r = f.result()
            # Cập nhật nếu tìm được kết quả tốt hơn
            if r and r[0] > best["val"]:
                best_val, loc, wh, s = r
                best.update(val=best_val, loc=loc, wh=wh, scale=s)

    # --- Giai đoạn tinh (fine search) ---
    # Xác định khoảng scale quanh kết quả thô để dò chi tiết hơn
    span = (scale_max - scale_min) / coarse_steps
    fine_min = max(scale_min, best["scale"] - span)
    fine_max = min(scale_max, best["scale"] + span)
    fine_scales = np.linspace(fine_min, fine_max, fine_steps)

    with ThreadPoolExecutor(max_workers=n_workers) as exe:
        futures = [exe.submit(match_at_scale, s) for s in fine_scales]
        for f in as_completed(futures):
            r = f.result()
            if r and r[0] > best["val"]:
                best_val, loc, wh, s = r
                best.update(val=best_val, loc=loc, wh=wh, scale=s)

    return best


def detect_template(
    image: np.ndarray,
    template_path: str,
    roi: Tuple[int, int, int, int],
    threshold: float = 0.5,
    hist_threshold: float = 0.01,
    scale_min: float = 1.0,
    scale_max: float = 10.0,
    coarse_steps: int = 8,
    fine_steps: int = 20,
    n_workers: int = None,
    annotate: bool = True
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    # Đọc template, ném lỗi nếu không tồn tại
    tpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        raise ValueError(f"Không tìm thấy template: {template_path}")

    # Lấy ROI từ ảnh gốc
    x0, y0, w, h = roi
    gray_full = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_roi  = gray_full[y0:y0+h, x0:x0+w]

    # Gọi hàm match và đo thời gian
    start = time.time()
    best = multi_scale_template_match(
        gray_roi, tpl,
        scale_min, scale_max,
        coarse_steps, fine_steps,
        n_workers
    )
    match_time = time.time() - start

    # Kiểm tra điểm match so với threshold
    if best["val"] < threshold:
        raise ValueError(
            f"Không có kết quả match đủ {threshold}, điểm cao nhất={best['val']:.2f}"
        )

    # Tính tọa độ thực tế của vùng match
    bx, by = best["loc"]
    bw, bh = best["wh"]
    patch = gray_roi[by:by+bh, bx:bx+bw]

    # Tính histogram so sánh giữa template gốc và patch
    hist_tpl   = cv2.calcHist([tpl],     [0], None, [256], [0, 256])
    hist_patch = cv2.calcHist([patch],   [0], None, [256], [0, 256])
    cv2.normalize(hist_tpl,   hist_tpl)
    cv2.normalize(hist_patch, hist_patch)
    hist_corr = cv2.compareHist(hist_tpl, hist_patch, cv2.HISTCMP_CORREL)
    if hist_corr < hist_threshold:
        raise ValueError(
            f"Histogram không đủ tin cậy: {hist_corr:.2f} < {hist_threshold}"
        )

    # Chuẩn bị dict thông tin kết quả
    info = {
        "roi": roi,
        "top_left":     (x0 + bx, y0 + by),
        "bottom_right": (x0 + bx + bw, y0 + by + bh),
        "match_score":  best["val"],
        "hist_corr":    hist_corr,
        "scale":        best["scale"],
        "template_size": best["wh"],
        "match_time":    match_time,
    }

    # Nếu cần annotate, vẽ khung và ghi note
    if annotate:
        annotated = image.copy()
        cv2.rectangle(annotated, info["top_left"], info["bottom_right"], (0,255,0), 3)
        note = f"{best['val']:.2f}@×{best['scale']:.2f} | h={hist_corr:.2f}"
        cv2.putText(annotated, note,
                    (info["top_left"][0], info["top_left"][1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        return annotated, info

    # Nếu không annotate, chỉ trả về None và info
    return None, info
