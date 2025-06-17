import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Dict, Any, Optional

from constants import (
THRESHOLD,HIST_THRESHOLD,
SCALE_MIN,
SCALE_MAX,
COARSE_STEPS,
FINE_STEPS,
SAVE_IMAGE
)

def detect_template(
    image: np.ndarray,
    template_path: str,
    roi: Tuple[int, int, int, int],
    threshold: float = THRESHOLD,
    hist_threshold: float = HIST_THRESHOLD,
    scale_min: float = SCALE_MIN,
    scale_max: float = SCALE_MAX,
    coarse_steps: int = COARSE_STEPS,
    fine_steps: int = FINE_STEPS,
    n_workers: int = 1,
    annotate: bool = SAVE_IMAGE
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    tpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        raise ValueError(f"Không tìm thấy template: {template_path}")

    x0, y0, w, h = roi
    gray_full = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_roi  = gray_full[y0:y0+h, x0:x0+w]

    start = time.time()
    best = multi_scale_template_match(
        gray_roi, tpl,
        scale_min, scale_max,
        coarse_steps, fine_steps,
        n_workers
    )
    match_time = time.time() - start

    bx, by = best["loc"]
    bw, bh = best["wh"]
    x1, y1 = x0 + bx,       y0 + by
    x2, y2 = x1 + bw,       y1 + bh
    patch = gray_roi[by:by+bh, bx:bx+bw]

    if best["val"] < threshold:
        raise ValueError(
            f"Match score {best['val']:.2f} < threshold {threshold:.2f}",
            x1, y1, x2, y2
        )



   

    # so sánh histogram
    hist_tpl   = cv2.calcHist([tpl],     [0], None, [256], [0, 256])
    hist_patch = cv2.calcHist([patch],   [0], None, [256], [0, 256])
    cv2.normalize(hist_tpl,   hist_tpl)
    cv2.normalize(hist_patch, hist_patch)
    hist_corr = cv2.compareHist(hist_tpl, hist_patch, cv2.HISTCMP_CORREL)
    if hist_corr < hist_threshold:
        raise ValueError(
            f"Histogram corr {hist_corr:.2f} < hist_threshold {hist_threshold:.2f}",
            x1, y1, x2, y2
        )

    info = {
        "roi": roi,
        "top_left":     (x1, y1),
        "bottom_right": (x2, y2),
        "match_score":  best["val"],
        "hist_corr":    hist_corr,
        "scale":        best["scale"],
        "template_size": best["wh"],
        "match_time":    match_time,
    }
    # print()
    # print('==========================')
    # print('match_score', info["match_score"])
    # print('hist_corr', info["hist_corr"])
    # print('==========================\n')

    if annotate:
        annotated = image.copy()
        cv2.rectangle(annotated, info["top_left"], info["bottom_right"], (0,255,0), 3)
        note = f"{best['val']:.2f}@×{best['scale']:.2f} | h={hist_corr:.2f}"
        cv2.putText(annotated, note,
                    (info["top_left"][0], info["top_left"][1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        return annotated, info

    return None, info



def multi_scale_template_match(
    gray_roi: np.ndarray,
    tpl: np.ndarray,
    scale_min: float = 0.5,
    scale_max: float = 10.0,
    coarse_steps: int = 15,
    fine_steps: int = 20,
    n_workers: int = 1,
) -> Dict[str, Any]:
    """
    Tìm template trên gray_roi theo scale, dùng tìm kiếm 2 giai đoạn và parallel.
    Trả về dict: { val, loc, wh, scale } với kết quả tốt nhất.
    """
    h0, w0 = tpl.shape
    gray_f = gray_roi.astype(np.float32)
    tpl_f   = tpl.astype(np.float32)

    def match_at_scale(s: float):
        w, h = int(w0 * s), int(h0 * s)
        if w < 20 or h < 20 or w > gray_roi.shape[1] or h > gray_roi.shape[0]:
            return None
        tpl_rs = cv2.resize(tpl_f, (w, h), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(gray_f, tpl_rs, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        return max_val, max_loc, (w, h), s

    # --- Giai đoạn thô (coarse) ---
    coarse_scales = np.linspace(scale_min, scale_max, coarse_steps)
    best_val = -1.0
    best = {"val": best_val, "loc": None, "wh": (w0, h0), "scale": 1.0}

    with ThreadPoolExecutor(max_workers=n_workers) as exe:
        futures = [exe.submit(match_at_scale, s) for s in coarse_scales]
        for f in as_completed(futures):
            r = f.result()
            if r and r[0] > best["val"]:
                best_val, loc, wh, s = r
                best.update(val=best_val, loc=loc, wh=wh, scale=s)

    # --- Giai đoạn tinh (fine) quanh scale tốt nhất ---
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




