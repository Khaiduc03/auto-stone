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
            encoding="gbk",
            errors="ignore"
        )
    except subprocess.CalledProcessError:
        return {}

    reader = csv.reader(StringIO(output))
    instances = {}
    for row in reader:
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
    def __init__(self, device_id, name, interval=5, on_stop=None):
        super().__init__()
        self.device_id = device_id
        self.name = name
        self.interval = interval
        self._stop_event = threading.Event()
        self._ruby_counter = 3
        self.on_stop = on_stop  # callback khi thread dừng

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
        if self.on_stop:
            self.on_stop(self.device_id)

    def stop(self):
        self._stop_event.set()

# --- GUI chính ---
class VMManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Virtual Machine Manager")
        self.threads = {}
        self.status_labels = {}

        device_ids = get_connected_devices()
        if not device_ids:
            messagebox.showerror("Lỗi", "Không tìm thấy thiết bị ADB nào.")
            self.destroy()
            return

        # Các control chung: Start All / Stop All
        control_frame = ttk.Frame(self, padding=5)
        control_frame.grid(row=0, column=0, sticky="w")
        btn_start_all = ttk.Button(control_frame, text="Start All", command=self.start_all)
        btn_start_all.pack(side="left", padx=5)
        btn_stop_all = ttk.Button(control_frame, text="Stop All", command=self.stop_all)
        btn_stop_all.pack(side="left", padx=5)

        # Danh sách VM
        for idx, device_id in enumerate(device_ids, start=1):
            name = get_ldplayer_instance_name(device_id)
            frame = ttk.Frame(self, padding=5)
            frame.grid(row=idx, column=0, sticky="w")

            lbl_name = ttk.Label(frame, text=f"{name}", width=25)
            lbl_name.pack(side="left")

            status = ttk.Label(frame, text="Stopped", width=10, foreground="red")
            status.pack(side="left", padx=5)
            self.status_labels[device_id] = status

            btn_start = ttk.Button(frame, text="Start",
                                   command=lambda d=device_id: self.start_monitor(d))
            btn_start.pack(side="left", padx=5)

            btn_stop = ttk.Button(frame, text="Stop",
                                  command=lambda d=device_id: self.stop_monitor(d))
            btn_stop.pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_monitor(self, device_id):
        # Nếu đang chạy, bỏ qua
        if device_id in self.threads and self.threads[device_id].is_alive():
            print(f"{device_id} đang chạy rồi.")
            return
        name = get_ldplayer_instance_name(device_id)
        # Cập nhật giao diện
        self.status_labels[device_id].config(text="Running", foreground="green")
        # Tạo thread với callback cập nhật status khi dừng
        t = MonitorThread(device_id, name, on_stop=self._on_thread_stop)
        t.daemon = True
        t.start()
        self.threads[device_id] = t
        print(f"Đã start {name}")

    def stop_monitor(self, device_id):
        t = self.threads.get(device_id)
        if t and t.is_alive():
            t.stop()
            print(f"Đang stop {device_id}...")
        else:
            print(f"{device_id} không đang chạy.")

    def start_all(self):
        for device_id in list(self.status_labels.keys()):
            self.start_monitor(device_id)

    def stop_all(self):
        for device_id in list(self.threads.keys()):
            self.stop_monitor(device_id)

    def _on_thread_stop(self, device_id):
        # Callback khi thread kết thúc
        if device_id in self.status_labels:
            self.status_labels[device_id].config(text="Stopped", foreground="red")
        print(f"Đã stop {device_id}")

    def on_close(self):
        for t in self.threads.values():
            if t.is_alive():
                t.stop()
                t.join()
        self.destroy()

if __name__ == "__main__":
    app = VMManagerApp()
    app.mainloop()
