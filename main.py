from sovle_quiz import main_resolve_quiz, sovle_capchav2, tap_capcha, uiauto_tap
from adb_utils import adb_screencap, get_connected_devices
import time
from auto_ruby import auto_click_ruby_box, auto_enter_dungeon



def monitor_loop(device_id, interval_sec=1):
    print(f"[Giám sát] Bắt đầu theo dõi {device_id}...")
    time_sleep_click_ruby = 0
    while True:
        try:
            screen = adb_screencap(device_id=device_id)
            main_resolve_quiz(device_id, screen)
            auto_enter_dungeon(device_id, screen)
            if(time_sleep_click_ruby == 30):
               auto_click_ruby_box(device_id)
               time_sleep_click_ruby = 0
            else:
                time_sleep_click_ruby += 1
            
        except Exception as e:
            print(f"[{device_id}] Lỗi: {e}")

        time.sleep(interval_sec)






if __name__ == "__main__":

    import sys
    import threading
    # screen = adb_screencap(device_id='emulator-5556')
    # tap_capcha('emulator-5556',screen)
    #main_resolve_quiz('emulator-5556', screen)
    #auto_click_ruby_box('emulator-5556')
    # device_ids = get_connected_devices()
    device_ids = ['emulator-5556']
    if not device_ids:
        print("❌ Không tìm thấy thiết bị ADB nào.")
        sys.exit(1)

    print(f"✅ Đã phát hiện {len(device_ids)} thiết bị: {device_ids}")


    threads = []
    for device_id in device_ids:
        t = threading.Thread(target=monitor_loop, args=(device_id,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    


    # # In tổng thời gian
    # print(f"Tổng thời gian: {time.time() - start_time:.2f} giây")
