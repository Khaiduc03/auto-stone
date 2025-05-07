import threading
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from io import StringIO

from adb_utils import get_connected_devices, adb_screencap
from auto_ruby import auto_click_ruby_box, auto_enter_dungeon
from sovle_quiz import main_resolve_quiz

# --- Helper để parse port từ device_id ---
def extract_port(device_id):
    """
    Hỗ trợ cả hai dạng:
      - 'emulator-5556'
      - '127.0.0.1:5556'
    Trả về int port hoặc None nếu không parse được.
    """
    if ':' in device_id:
        port_str = device_id.rsplit(':', 1)[1]
    elif '-' in device_id:
        port_str = device_id.rsplit('-', 1)[1]
    else:
        return None

    try:
        return int(port_str)
    except ValueError:
        return None

# --- Lấy map index → name (chỉ chạy 1 lần) ---
def list_ldplayer_instances(ldconsole_path=r"C:\LDPlayer\LDPlayer4\ldconsole.exe"):
    """
    Chạy ldconsole list2, decode với GBK (để tránh '?????'),
    parse CSV và trả về dict: { index: name }
    """
    try:
        output = subprocess.check_output(
            [ldconsole_path, "list2"],
            encoding="gbk",    # GBK để giữ nguyên ký tự đa byte
            errors="ignore"
        )
    except subprocess.CalledProcessError:
        return {}

    reader = csv.reader(StringIO(output))
    instances = {}
    for row in reader:
        # row[0]: index, row[1]: name
        if len(row) >= 2 and row[0].isdigit():
            idx = int(row[0])
            name = row[1].strip()
            instances[idx] = name
    return instances

# Build map ngay khi import
_LDPLAYER_MAP = list_ldplayer_instances()

# --- Hàm lấy tên từ device_id ---
def get_ldplayer_instance_name(device_id):
    port = extract_port(device_id)
    if port is None:
        return device_id

    idx = (port - 5554) // 2
    return _LDPLAYER_MAP.get(idx, device_id)

# --- Thread giám sát ---
class MonitorThread(threading.Thread):
    def __init__(self, device_id, name, interval=3):
        super().__init__()
        self.device_id = device_id
        self.name = name
        self.interval = interval
        self._stop_event = threading.Event()
        self._ruby_counter = 0

    def run(self):
        print(f"[Giám sát] Bắt đầu theo dõi {self.name} ({self.device_id})")
        while not self._stop_event.is_set():
            try:
                screen = adb_screencap(device_id=self.device_id)
                auto_enter_dungeon(self.device_id, screen)
                main_resolve_quiz(self.device_id, screen, self.name)
                if self._ruby_counter >= 3:
                    auto_click_ruby_box(self.device_id)
                    self._ruby_counter = 0
                else:
                    self._ruby_counter += 1
            except Exception as e:
                print(f"[{self.name}] Lỗi: {e}")
            time.sleep(self.interval)
        print(f"[Giám sát] Dừng theo dõi {self.name}")

    def stop(self):
        self._stop_event.set()

# --- GUI chính ---
class VMManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Virtual Machine Manager")
        self.threads = {}

        device_ids = get_connected_devices()
        if not device_ids:
            messagebox.showerror("Lỗi", "Không tìm thấy thiết bị ADB nào.")
            self.destroy()
            return

        for row, device_id in enumerate(device_ids):
            name = get_ldplayer_instance_name(device_id)
            frame = ttk.Frame(self, padding=5)
            frame.grid(row=row, column=0, sticky="w")

            lbl = ttk.Label(frame, text=f"{name}", width=30)
            lbl.pack(side="left")

            btn_start = ttk.Button(
                frame, text="Start",
                command=lambda d=device_id: self.start_monitor(d)
            )
            btn_start.pack(side="left", padx=5)

            btn_stop = ttk.Button(
                frame, text="Stop",
                command=lambda d=device_id: self.stop_monitor(d)
            )
            btn_stop.pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_monitor(self, device_id):
        if device_id in self.threads and self.threads[device_id].is_alive():
            print(f"{device_id} đang chạy rồi.")
            return
        name = get_ldplayer_instance_name(device_id)
        t = MonitorThread(device_id, name)
        t.daemon = True
        t.start()
        self.threads[device_id] = t
        print(f"Đã start {name}")

    def stop_monitor(self, device_id):
        t = self.threads.get(device_id)
        if t and t.is_alive():
            t.stop()
            t.join()
            print(f"Đã stop {device_id}")
        else:
            print(f"{device_id} không đang chạy.")

    def on_close(self):
        for t in self.threads.values():
            if t.is_alive():
                t.stop()
                t.join()
        self.destroy()

if __name__ == "__main__":
    app = VMManagerApp()
    app.mainloop()
