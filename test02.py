#!/usr/bin/env python3
import subprocess, sys
import numpy as np, cv2

# ==== CẤU HÌNH TẠI ĐÂY ====
TEMPLATE_PATH = "shiba.png"           # file template đã crop
DEVICE_ID     = None # hoặc None nếu chỉ có 1 thiết bị
ROI           = (80, 0, 1000, 2000) # x0, y0, width, height
THRESHOLD     = 0.4                # ngưỡng matchTemplate
SCALE_MIN     = 1               # scale nhỏ nhất
SCALE_MAX     =10            # scale lớn nhất
SCALE_STEPS   = 20                   # số bước scale
OUTPUT_PATH   = "debug.png"          # file lưu ảnh kết quả
# ============================

def adb_screencap(device_id=None):
    cmd = ["adb"] + (["-s", device_id] if device_id else []) + \
          ["exec-out", "screencap", "-p"]
    raw = subprocess.check_output(cmd)
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        print("❌ Lỗi decode screenshot", file=sys.stderr)
        sys.exit(1)
    return img

def multi_scale_template_match(gray_roi, tpl):
    h0, w0 = tpl.shape
    best = {"val":-1, "loc":None, "wh":(w0,h0), "scale":1.0}
    for s in np.linspace(SCALE_MIN, SCALE_MAX, SCALE_STEPS):
        w, h = int(w0*s), int(h0*s)
        if w < 10 or h < 10 or w > gray_roi.shape[1] or h > gray_roi.shape[0]:
            continue
        tpl_rs = cv2.resize(tpl, (w, h), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(gray_roi, tpl_rs, cv2.TM_CCOEFF_NORMED)
        _, mx, _, pt = cv2.minMaxLoc(res)
        if mx > best["val"]:
            best.update(val=mx, loc=pt, wh=(w,h), scale=s)
    return best

def main():
    # 1) Load template
    tpl = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        print(f"❌ Không tìm thấy template: {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)

    # 2) Screenshot
    full = adb_screencap(DEVICE_ID)
    gray_full = cv2.cvtColor(full, cv2.COLOR_BGR2GRAY)

    # 3) Crop ROI
    x0, y0, w, h = ROI
    x1, y1 = x0+w, y0+h
    gray_roi = gray_full[y0:y1, x0:x1]

    # 4) Multi-scale match
    best = multi_scale_template_match(gray_roi, tpl)

    if best["val"] < THRESHOLD:
        print(f"⚠️ Không tìm thấy match ≥ {THRESHOLD} (max={best['val']:.2f})")
        sys.exit(1)

    # 5) Tính tọa độ global
    bx, by    = best["loc"]
    bw, bh    = best["wh"]
    top_left     = (x0 + bx, y0 + by)
    bottom_right = (top_left[0] + bw, top_left[1] + bh)

    # 6) Vẽ khung lên full‐color image
    cv2.rectangle(full, top_left, bottom_right, (0,255,0), 3)
    note = f"{best['val']:.2f}@×{best['scale']:.2f}"
    cv2.putText(full, note, (top_left[0], top_left[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    # 7) Lưu ảnh và in thông tin
    cv2.imwrite(OUTPUT_PATH, full)
    print("✅ Đã lưu debug image →", OUTPUT_PATH)
    print("   ROI              =", ROI)
    print("   Match top-left     =", top_left)
    print("   Match bottom-right =", bottom_right)
    print("   Template size      =", best["wh"])
    print("   Confidence         =", best["val"])
    print("   Used scale         =", best["scale"])

if __name__ == "__main__":
    main()
