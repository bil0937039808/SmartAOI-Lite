import cv2
import numpy as np
import os
from datetime import datetime
from pathlib import Path
RESULT_FOLDER = "result_input/"
def inspect_image(image_path: str) -> dict | None:
    img = cv2.imread(image_path)
    if img is None:
        print(f"無法讀取影像: {image_path}")
        return None
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    print(f"結果資料夾: {RESULT_FOLDER}")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0,   100, 100])
    upper_red1 = np.array([10,  255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) |  cv2.inRange(hsv, lower_red2, upper_red2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask_black = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY_INV)
    combined_mask = cv2.bitwise_or(mask_red, mask_black)
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    defect_area = 0
    defect_positions = []
    type_index=0
    result = "PASS"
    AREA_THRESHOLD = 90  # 像素門檻
    for c in contours:
        area = cv2.contourArea(c)
        if area > AREA_THRESHOLD:
            defect_area += area
            result = "FAIL"
            x, y, w, h = cv2.boundingRect(c)
            defect_positions.append((x, y, w, h, type_index))
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        type_index=type_index+1

    if result == "FAIL":
        base, ext = os.path.splitext(image_path)
        file_name = Path(base).name
        result_path = RESULT_FOLDER+f"{file_name}_result{ext}"
        cv2.imwrite(result_path, img)
        print(f"[INFO] 瑕疵標記圖已儲存: {result_path}")
    sn_id = os.path.splitext(os.path.basename(image_path))[0]

    return {"sn_id": sn_id,"inspect_result": result,"defect_area":int(defect_area), "defect_positions": defect_positions
            ,"timestamp":datetime.now().isoformat(),}


if __name__ == "__main__":
    TEST_IMAGE = ".\image\pngtree-the-integrated-circuit-board-png-image_33877023.jpg"          
    if os.path.exists(TEST_IMAGE):
        result = inspect_image(TEST_IMAGE)
        print("結果", result)
    else:
        print(f"找不到{TEST_IMAGE}")