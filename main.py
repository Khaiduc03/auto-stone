import json
import subprocess
from sovle_quiz import main_resolve_quiz, sovle_capchav2, tap_capcha, uiauto_tap
from adb_utils import adb_screencap, get_connected_devices
import time
from auto_ruby import auto_click_ruby_box, auto_enter_dungeon



def monitor_loop(device_id, interval_sec=3):
    name=  get_ldplayer_instance_name(device_id)
    print(f"[Giám sát] Bắt đầu theo dõi {name}...")
    time_sleep_click_ruby = 0
    while True:
        try:
            screen = adb_screencap(device_id=device_id)
            auto_enter_dungeon(device_id, screen)
            main_resolve_quiz(device_id, screen,name)
         
            if(time_sleep_click_ruby == 3):
               auto_click_ruby_box(device_id)
               time_sleep_click_ruby = 0
            else:
                time_sleep_click_ruby += 1
            # print(f"[Giám sát] Bắt đầu theo dõi {device_id}...")
        except Exception as e:
            print(f"[{name}] Lỗi: {e}")

        time.sleep(interval_sec)




def get_ldplayer_instance_name(device_id,
        ldconsole_path=r"C:\LDPlayer\LDPlayer4\ldconsole.exe"):
    """
    Với device_id dạng 'emulator-xxxx', sẽ:
      1) tách port = xxxx
      2) tính index = (port - 5554) // 2
      3) chạy `ldconsole list2` (trả CSV), tìm dòng có index ấy, và trả về tên (cột 2)
    """
    # 1) lấy port
    try:
        port = int(device_id.split('-')[-1])
    except ValueError:
        return None

    # 2) tính index tương ứng với LDPlayer
    instance_index = (port - 5554) // 2

    # 3) gọi ldconsole list2 để lấy CSV
    try:
        output = subprocess.check_output(
            [ldconsole_path, "list2"],
            encoding="utf-8",
            errors="ignore"
        )
    except subprocess.CalledProcessError:
        return None

    # parse từng dòng CSV
    for line in output.splitlines():
        parts = line.split(",")
        if len(parts) < 2:
            continue
        try:
            idx = int(parts[0])
        except ValueError:
            continue
        if idx == instance_index:
            return parts[1].strip()
    return None

if __name__ == "__main__":

    import sys
    import threading
   
    device_ids = get_connected_devices()
    #device_ids = ['emulator-5556']
    if not device_ids:
        print("❌ Không tìm thấy thiết bị ADB nào.")
        sys.exit(1)

    print(f"✅ Đã phát hiện {len(device_ids)} thiết bị: {device_ids}")

    # threads = []
    # for device_id in device_ids:
    #     name=  get_ldplayer_instance_name(device_id)
    #     if name is None:
    #         print(f"❌ Không tìm thấy tên thiết bị cho {device_id}.")
    #         continue
    #     print(f"✅ Tên thiết bị {device_id}: {name}")


        # Chạy vòng lặp giám sát trong một luồng riêng biệt
        # t = threading.Thread(target=monitor_loop, args=(device_id, 5))
        # t.start()
        # threads.append(t)

    threads = []
    for device_id in device_ids:
        t = threading.Thread(target=monitor_loop, args=(device_id,5))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    



 # screen = adb_screencap(device_id='emulator-5556')
    # tap_capcha('emulator-5556',screen)
    #main_resolve_quiz('emulator-5556', screen)
    #auto_click_ruby_box('emulator-5556')
    # # In tổng thời gian
    # print(f"Tổng thời gian: {time.time() - start_time:.2f} giây")
