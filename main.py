import threading
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from io import StringIO

import uiautomator2 as u2
from adb_utils import adb_screencap_adb, get_connected_devices
from auto_ruby import auto_click_ruby_box, auto_enter_dungeon
from sovle_quiz import main_resolve_quiz
import gc

# --- Helper để parse port từ device_id ---
def extract_port(device_id):
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

# --- Lấy map index → name trên LDPlayer ---
def list_ldplayer_instances(ldconsole_path=r"C:\LDPlayer\LDPlayer4\ldconsole.exe"):
    try:
        output = subprocess.check_output(
            [ldconsole_path, "list2"], encoding="gbk", errors="ignore"
        )
    except subprocess.CalledProcessError:
        return {}
    reader = csv.reader(StringIO(output))
    instances = {}
    for row in reader:
        if len(row) >= 2 and row[0].isdigit():
            instances[int(row[0])] = row[1].strip()
    return instances

_LDPLAYER_MAP = list_ldplayer_instances()

def get_ldplayer_instance_name(device_id):
    port = extract_port(device_id)
    if port is None:
        return device_id
    idx = (port - 5554) // 2
    return _LDPLAYER_MAP.get(idx, device_id)

# --- Thread giám sát mỗi VM ---
class MonitorThread(threading.Thread):
    def __init__(
        self,
        device_id,
        name,
        auto_dungeon=False,
        auto_ruby=False,
        auto_captcha=False,
        interval=5,
        on_stop=None
    ):
        super().__init__()
        self.device_id = device_id
        self.name = name
        self.interval = interval
        self.auto_dungeon = auto_dungeon
        self.auto_ruby = auto_ruby
        self.auto_captcha = auto_captcha
        self._stop_event = threading.Event()
        self._ruby_counter = 3
        self.on_stop = on_stop

        # ---- TẠO KẾT NỐI U2 ----
        try:
            self.u2 = u2.connect_usb(self.device_id)
        except Exception:
            self.u2 = u2.connect(self.device_id)
        print(f"[{self.name}] u2 connected: {self.u2.device_info}")

    def set_auto_dungeon(self, enabled: bool):
        self.auto_dungeon = enabled
        print(f"[{self.name}] Auto Dungeon set to {enabled}")
    def set_auto_ruby(self, enabled: bool):
        self.auto_ruby = enabled
        print(f"[{self.name}] Auto Ruby set to {enabled}")
    def set_auto_captcha(self, enabled: bool):
        self.auto_captcha = enabled
        print(f"[{self.name}] Auto Captcha set to {enabled}")

    def run(self):
        print(f"[Giám sát] Bắt đầu theo dõi {self.name} ({self.device_id})")
        while not self._stop_event.is_set():
            try:
                # vẫn chụp bằng adb_screencap_adb
                screen = adb_screencap_adb(device_id=self.device_id)

                if self.auto_dungeon:
                    # truyền thêm self.u2 ở cuối
                    auto_enter_dungeon(self.device_id, screen, self.u2)
                if self.auto_captcha:
                    main_resolve_quiz(self.device_id, screen, self.name, self.u2)
                if self.auto_ruby:
                    if self._ruby_counter >= 3:
                        auto_click_ruby_box(self.device_id, self.u2)
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
        self.auto_dungeon_vars = {}
        self.auto_ruby_vars = {}
        self.auto_captcha_vars = {}

        control_frame = ttk.Frame(self, padding=5)
        control_frame.grid(row=0, column=0, sticky="w")
        ttk.Button(control_frame, text="Start All", command=self.start_all).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Stop All",  command=self.stop_all).pack(side="left", padx=5)

        device_ids = get_connected_devices()
        if not device_ids:
            messagebox.showerror("Lỗi", "Không tìm thấy thiết bị ADB nào.")
            self.destroy()
            return

        for idx, device_id in enumerate(device_ids, start=1):
            name = get_ldplayer_instance_name(device_id)
            frame = ttk.Frame(self, padding=5)
            frame.grid(row=idx, column=0, sticky="w")

            self.auto_dungeon_vars[device_id] = tk.BooleanVar(value=True)
            self.auto_ruby_vars[device_id]   = tk.BooleanVar(value=True)
            self.auto_captcha_vars[device_id]= tk.BooleanVar(value=True)

            ttk.Label(frame, text=f"{idx} - {name}", width=25).pack(side="left")
            ttk.Checkbutton(frame, text="Dungeon",
                variable=self.auto_dungeon_vars[device_id],
                command=lambda d=device_id: self._toggle_dungeon(d)
            ).pack(side="left", padx=2)
            ttk.Checkbutton(frame, text="Ruby",
                variable=self.auto_ruby_vars[device_id],
                command=lambda d=device_id: self._toggle_ruby(d)
            ).pack(side="left", padx=2)
            ttk.Checkbutton(frame, text="Captcha",
                variable=self.auto_captcha_vars[device_id],
                command=lambda d=device_id: self._toggle_captcha(d)
            ).pack(side="left", padx=2)

            status = ttk.Label(frame, text="Stopped", width=10, foreground="red")
            status.pack(side="left", padx=5)
            self.status_labels[device_id] = status

            ttk.Button(frame, text="Start", command=lambda d=device_id: self.start_monitor(d)).pack(side="left", padx=5)
            ttk.Button(frame, text="Stop",  command=lambda d=device_id: self.stop_monitor(d)).pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _toggle_dungeon(self, device_id):
        t = self.threads.get(device_id)
        if t and t.is_alive():
            t.set_auto_dungeon(self.auto_dungeon_vars[device_id].get())

    def _toggle_ruby(self, device_id):
        t = self.threads.get(device_id)
        if t and t.is_alive():
            t.set_auto_ruby(self.auto_ruby_vars[device_id].get())

    def _toggle_captcha(self, device_id):
        t = self.threads.get(device_id)
        if t and t.is_alive():
            t.set_auto_captcha(self.auto_captcha_vars[device_id].get())

    def start_monitor(self, device_id):
        if device_id in self.threads and self.threads[device_id].is_alive():
            return
        self.status_labels[device_id].config(text="Running", foreground="green")
        t = MonitorThread(
            device_id,
            get_ldplayer_instance_name(device_id),
            auto_dungeon=self.auto_dungeon_vars[device_id].get(),
            auto_ruby=self.auto_ruby_vars[device_id].get(),
            auto_captcha=self.auto_captcha_vars[device_id].get(),
            on_stop=self._on_thread_stop
        )
        t.daemon = True
        t.start()
        self.threads[device_id] = t

    def stop_monitor(self, device_id):
        t = self.threads.get(device_id)
        if t and t.is_alive():
            t.stop()

    def start_all(self):
        for idx, device_id in enumerate(self.auto_dungeon_vars):
            self.after(idx * 7000, lambda d=device_id: self.start_monitor(d))

    def stop_all(self):
        for did in list(self.threads):
            self.stop_monitor(did)

    def _on_thread_stop(self, device_id):
        if device_id in self.status_labels:
            self.status_labels[device_id].config(text="Stopped", foreground="red")

    def on_close(self):
        for t in self.threads.values():
            if t.is_alive():
                t.stop()
                t.join()
        self.destroy()


if __name__ == "__main__":
    VMManagerApp().mainloop()
