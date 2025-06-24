#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import Tuple

import cv2
import numpy as np

from adb_utils import adb_screencap_adb


def crop_screen_by_roi( roi: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop a screenshot numpy array according to ROI (x, y, w, h).

    Args:
        screen: full-screen image as a numpy array (H x W x C).
        roi: tuple (x, y, width, height), with (0,0) at top-left.

    Returns:
        Cropped image as numpy array.
    """
    #get screen by adb
    screen = adb_screencap_adb()
    if screen is None:
        raise ValueError("Failed to capture screen")

    x, y, w, h = roi
    return screen[y:y+h, x:x+w]

class GridROI:
    """
    Quản lý ROI cho lưới các ô chữ nhật với gap xen kẽ.

    - start: (x0, y0) của ô (1,1) trong lưới 1-based
    - cell_size: (width, height) mỗi ô
    - grid_dim: (cols, rows) số cột và số hàng
    - gap_x: khoảng cách ngang cố định giữa các ô
    - gap_even_to_odd: khoảng cách dọc khi đi từ hàng chẵn → lẻ
    - gap_odd_to_even: khoảng cách dọc khi đi từ hàng lẻ → chẵn

    Phương thức get_cell nhận (col, row) 1-based và trả về ROI zero-based
    dưới dạng (x0, y0, width, height).
    """
    def __init__(
        self,
        start: Tuple[int, int],
        cell_size: Tuple[int, int],
        grid_dim: Tuple[int, int],
        gap_x: int = 1,
        gap_even_to_odd: int = 2,
        gap_odd_to_even: int = 1,
    ):
        self.start_x, self.start_y = start
        self.cell_w, self.cell_h = cell_size
        self.cols, self.rows = grid_dim
        self.gap_x = gap_x
        self.gap_even_to_odd = gap_even_to_odd
        self.gap_odd_to_even = gap_odd_to_even

    def _vertical_gap_after(self, row_idx: int) -> int:
        """Gap dọc sau hàng row_idx (zero-based) khi đi xuống hàng kế."""
        return (
            self.gap_even_to_odd
            if row_idx % 2 == 0
            else self.gap_odd_to_even
        )

    def _get_cell_zero(self, col_idx: int, row_idx: int) -> Tuple[int, int, int, int]:
        """Tính ROI cho ô tại chỉ số zero-based (col_idx, row_idx)."""
        # X-coordinate
        x0 = self.start_x + col_idx * (self.cell_w + self.gap_x)

        # Y-offset: cộng dồn từng hàng trước row_idx
        y_offset = 0
        for r in range(row_idx):
            y_offset += self.cell_h
            y_offset += self._vertical_gap_after(r)
        y0 = self.start_y + y_offset

        return (x0, y0, self.cell_w, self.cell_h)

    def get_cell(self, col: int, row: int) -> Tuple[int, int, int, int]:
        """
        Trả về ROI (x0, y0, w, h) cho ô tại:
         - cột `col` trong [1..cols]
         - hàng `row` trong [1..rows]
        """
        if not (1 <= col <= self.cols):
            raise ValueError(f"col phải trong [1,{self.cols}]")
        if not (1 <= row <= self.rows):
            raise ValueError(f"row phải trong [1,{self.rows}]")
        # chuyển sang zero-based
        return self._get_cell_zero(col - 1, row - 1)


if __name__ == "__main__":
    # Bạn có 8 cột và 4 hàng; ô nhỏ 112×111; start=(39,1790)
    grid = GridROI(
        start=(40, 1790),
        cell_size=(111, 111),
        grid_dim=(8, 4),          # 8 cột, 4 hàng
        gap_x=1,                  # gap ngang 1px
        gap_even_to_odd=2,        # từ hàng chẵn→lẻ: +2px
        gap_odd_to_even=1,        # từ hàng lẻ→chẵn: +1px
    )

    # Ví dụ: col=1, row=2 (tức ô cột 1, hàng 2 theo 1-based)
    col, row = 1, 2
    roi = grid.get_cell(col, row)
    print(f"Cell(col={col}, row={row}) → ROI = {roi}")

    # In thử toàn bộ lưới
    for r in range(1, grid.rows + 1):
        for c in range(1, grid.cols + 1):
            roi = grid.get_cell(c, r)
            cropped = crop_screen_by_roi(roi=roi)
            out_file = f"test_stone/roi_capture_r{r}_c{c}.png"
            if cv2.imwrite(out_file, cropped):
                print(f"Saved ROI {roi} to {out_file}")
            else:
                print(f"Failed to save ROI {roi} to {out_file}", file=sys.stderr)

