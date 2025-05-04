import cv2
import numpy as np
import time
from typing import Tuple, Dict, Any, Optional


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
    h0, w0 = tpl.shape
    best = {"val": -1.0, "loc": None, "wh": (w0, h0), "scale": 1.0}
    for s in np.linspace(scale_min, scale_max, scale_steps):
        w, h = int(w0 * s), int(h0 * s)
        if w < 10 or h < 10 or w > gray_roi.shape[1] or h > gray_roi.shape[0]:
            continue
        tpl_rs = cv2.resize(tpl, (w, h), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(gray_roi, tpl_rs, cv2.TM_CCOEFF_NORMED)
        _, mx, _, pt = cv2.minMaxLoc(res)
        if mx > best["val"]:
            best.update(val=mx, loc=pt, wh=(w, h), scale=s)
    return best


def detect_template(
    image: np.ndarray,
    template_path: str,
    roi: Tuple[int, int, int, int],
    threshold: float = 0.5,
    hist_threshold: float = 0.01,
    scale_min: float = 1.0,
    scale_max: float = 10.0,
    scale_steps: int = 20,
    annotate: bool = False
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    """
    Phát hiện template trong ảnh nhập vào (image) tại vùng ROI.
    Nếu annotate=True, trả về ảnh có vẽ khung; ngược lại chỉ trả về info.
    Trả về Tuple[annotated_image hoặc None, info_dict]
    """
    tpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        raise ValueError(f"Không tìm thấy template: {template_path}")

    x0, y0, w, h = roi
    gray_full = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_roi = gray_full[y0:y0+h, x0:x0+w]

    start_time = time.time()
    best = multi_scale_template_match(
        gray_roi, tpl, scale_min, scale_max, scale_steps
    )
    match_time = time.time() - start_time

    if best["val"] < threshold:
        raise ValueError(
            f"Không có kết quả match đủ {threshold}, điểm cao nhất={best['val']:.2f}"
        )

    bx, by = best["loc"]
    bw, bh = best["wh"]
    patch = gray_roi[by:by+bh, bx:bx+bw]

    hist_tpl = cv2.calcHist([tpl], [0], None, [256], [0, 256])
    hist_patch = cv2.calcHist([patch], [0], None, [256], [0, 256])
    cv2.normalize(hist_tpl, hist_tpl)
    cv2.normalize(hist_patch, hist_patch)
    hist_corr = cv2.compareHist(hist_tpl, hist_patch, cv2.HISTCMP_CORREL)
    if hist_corr < hist_threshold:
        raise ValueError(
            f"Histogram không đủ tin cậy: {hist_corr:.2f} < {hist_threshold}"
        )

    info = {
        "roi": roi,
        "top_left": (x0 + bx, y0 + by),
        "bottom_right": (x0 + bx + bw, y0 + by + bh),
        "match_score": best["val"],
        "hist_corr": hist_corr,
        "scale": best["scale"],
        "template_size": best["wh"],
        "match_time": match_time,
    }

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
        return annotated, info

    return None, info