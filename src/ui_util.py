import cv2
import numpy as np

class ImageWindow:
    """
    一個簡單的輔助類別，用於調整大小並顯示 OpenCV 影像。
    """
    def __init__(self, img, title, max_height=600):
        if img is None:
            print(f"Error: Image provided to ImageWindow '{title}' is None.")
            return

        # 保持長寬比
        try:
            h, w = img.shape[:2]
            if h > max_height:
                scale = max_height / h
                new_w = int(w * scale)
                new_h = int(h * scale)
                resized_image = cv2.resize(img, (new_w, new_h))
            else:
                resized_image = img
                
            cv2.imshow(title, resized_image)
            
        except Exception as e:
            print(f"Error displaying image '{title}': {e}")
            # 如果調整大小失敗 (例如 img 是空的)，也嘗試顯示原始影像
            try:
                cv2.imshow(title, img)
            except Exception as e_inner:
                print(f"Failed to show image '{title}' completely: {e_inner}")