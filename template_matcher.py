import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Dict, Any, Optional

from constants import (
    THRESHOLD,
    HIST_THRESHOLD,
    SCALE_MIN,
    SCALE_MAX,
    COARSE_STEPS,
    FINE_STEPS,
)

class TemplateMatcher:
    def __init__(
        self,
        template_path: str,
        roi: Tuple[int, int, int, int],
        threshold: float = THRESHOLD,
        hist_threshold: float = HIST_THRESHOLD,
        scale_min: float = SCALE_MIN,
        scale_max: float = SCALE_MAX,
        coarse_steps: int = COARSE_STEPS,
        fine_steps: int = FINE_STEPS,
        n_workers: int = None,
    ):
        """
        Khởi tạo TemplateMatcher với các tham số mặc định lấy từ constants.
        """
        # Load và chuẩn bị template
        tpl_gray = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if tpl_gray is None:
            raise ValueError(f"Không tìm thấy template: {template_path}")
        self.tpl_f = tpl_gray.astype(np.float32)
        self.h0, self.w0 = tpl_gray.shape

        # Histogram template (chuẩn hóa ngay)
        hist_tpl = cv2.calcHist([tpl_gray], [0], None, [256], [0,256])
        cv2.normalize(hist_tpl, hist_tpl, 0, 1, cv2.NORM_MINMAX)
        self.hist_tpl = hist_tpl

        # Lưu tham số\        
        self.roi = roi
        self.threshold = threshold
        self.hist_threshold = hist_threshold
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.coarse_steps = coarse_steps
        self.fine_steps = fine_steps
        self.n_workers = n_workers or 1

        # Executor dùng chung cho cả 2 giai đoạn
        self.executor = ThreadPoolExecutor(max_workers=self.n_workers)

    def _match_at_scale(self, gray_f: np.ndarray, s: float):
        w, h = int(self.w0 * s), int(self.h0 * s)
        if w < 20 or h < 20 or w > gray_f.shape[1] or h > gray_f.shape[0]:
            return None
        tpl_rs = cv2.resize(self.tpl_f, (w, h), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(gray_f, tpl_rs, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        return max_val, max_loc, (w, h), s

    def match(self, image: np.ndarray, annotate: bool = False) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        x0, y0, w, h = self.roi
        gray_full = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_roi  = gray_full[y0:y0+h, x0:x0+w]

        # Chuyển ROI sang float32
        gray_f = gray_roi.astype(np.float32)

        # Helper tìm best trong 1 list scales
        def search(scales, best):
            futures = {self.executor.submit(self._match_at_scale, gray_f, s): s for s in scales}
            for f in as_completed(futures):
                r = f.result()
                if r and r[0] > best['val']:
                    best.update(val=r[0], loc=r[1], wh=r[2], scale=r[3])
            return best

        # Giai đoạn coarse
        best = {"val": -1.0, "loc": (0,0), "wh": (self.w0,self.h0), "scale": 1.0}
        coarse_scales = np.linspace(self.scale_min, self.scale_max, self.coarse_steps)
        best = search(coarse_scales, best)

        # Giai đoạn fine
        span = (self.scale_max - self.scale_min) / self.coarse_steps
        fine_min = max(self.scale_min, best['scale'] - span)
        fine_max = min(self.scale_max, best['scale'] + span)
        fine_scales = np.linspace(fine_min, fine_max, self.fine_steps)
        best = search(fine_scales, best)

        # Tính thời gian match (nên đo bao gồm search)
        # [có thể thêm đo match_time nếu cần]

        bx, by = best['loc']
        bw, bh = best['wh']
        x1, y1 = x0 + bx, y0 + by
        x2, y2 = x1 + bw, y1 + bh
        patch = gray_roi[by:by+bh, bx:bx+bw]

        if best['val'] < self.threshold:
            raise ValueError(f"Match score {best['val']:.2f} < threshold {self.threshold:.2f}")

        # So sánh histogram patch và template
        hist_patch = cv2.calcHist([patch], [0], None, [256], [0,256])
        cv2.normalize(hist_patch, hist_patch, 0, 1, cv2.NORM_MINMAX)
        hist_corr = cv2.compareHist(self.hist_tpl, hist_patch, cv2.HISTCMP_CORREL)
        if hist_corr < self.hist_threshold:
            raise ValueError(f"Hist corr {hist_corr:.2f} < threshold {self.hist_threshold:.2f}")

        info = {
            'roi':          self.roi,
            'top_left':     (x1, y1),
            'bottom_right': (x2, y2),
            'match_score':  best['val'],
            'hist_corr':    hist_corr,
            'scale':        best['scale'],
            'template_size': best['wh'],
        }

        if annotate:
            out = image.copy()
            cv2.rectangle(out, info['top_left'], info['bottom_right'], (0,255,0), 3)
            note = f"{best['val']:.2f}@×{best['scale']:.2f} | h={hist_corr:.2f}"
            cv2.putText(out, note,
                        (info['top_left'][0], info['top_left'][1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            return out, info

        return None, info
