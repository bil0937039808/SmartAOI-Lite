import os
import time
import requests
from ImageRecognition import inspect_image
API_URL      = "http://localhost:8000/api/v1/line-capture"
WATCH_FOLDER = "./factory_cam_input"
POLL_INTERVAL = 1   # 秒
def send_to_api(data: dict) -> bool:
    try:
        resp = requests.post(API_URL, json=data, timeout=5)
        if resp.status_code == 200:
            print(f"OK:{data}")
            return True
        else:
            print(f"API錯誤{resp.status_code}: {resp.text}")
    except requests.exceptions.ConnectionError:
        print(f"無法連線{API_URL}")
    except Exception as e:
        print(f"異常:{e}")
    return False

def watch_and_process():
    os.makedirs(WATCH_FOLDER, exist_ok=True)
    print(f"資料夾:{WATCH_FOLDER}")
    processed = set()   
    while True:
        images = [
            os.path.join(WATCH_FOLDER, f)
            for f in os.listdir(WATCH_FOLDER)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
            and os.path.join(WATCH_FOLDER, f) not in processed
        ]
        for img_path in images:
            print(f"影像:{img_path}")
            data = inspect_image(img_path)
            if data:
                for item in data["defect_positions"]:
                    one_data={
                        "sn_id": data["sn_id"],
                        "inspect_result": data["inspect_result"],
                        "defect_area": data["defect_area"], 
                        "defect_position": (item[0], item[1], item[2], item[3], item[4]),
                    }
                    print(f"瑕疵位置: x={item[0]}, y={item[1]}, w={item[2]}, h={item[3]}, type={item[4]}")
                    send_to_api(one_data)
            else:
                print(f"辨識失敗: {img_path}")
            try:
                os.remove(img_path)
            except OSError as e:
                print(f"無法刪除檔案:{e}")
                processed.add(img_path)   
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        watch_and_process()
    except KeyboardInterrupt:
        print("\n監聽停止")
