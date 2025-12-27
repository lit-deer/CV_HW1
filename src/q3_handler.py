import cv2
import numpy as np
from PyQt5.QtWidgets import QMessageBox

# 匯入我們將建立的輔助工具
from src.ui_util import ImageWindow

class Q3_Handler:
    def __init__(self, main_window, base_data):
        # 儲存對主視窗 UI 的參考
        self.ui = main_window 
        # 儲存對共用資料的參考
        self.base = base_data 

    def stereo_disparity(self):
        # 1. 檢查圖片是否已載入
        if self.base.imageL is None or self.base.imageR is None:
            QMessageBox.warning(self.ui, "Warning", "Please load Image_L and Image_R first!")
            return
        
        print("=3.1 Stereo Disparity Map")

        # 2. 讀取灰階影像
        imgL = cv2.imread(self.base.imageL, cv2.IMREAD_GRAYSCALE)
        imgR = cv2.imread(self.base.imageR, cv2.IMREAD_GRAYSCALE)
        
        if imgL is None or imgR is None:
            QMessageBox.critical(self.ui, "Error", f"Failed to read {self.base.imageL} or {self.base.imageR}")
            return

        # 3. 計算視差 (根據 PDF 參數)
        stereo = cv2.StereoBM_create(numDisparities=432, blockSize=25)
        disparity = stereo.compute(imgL, imgR)
        
        # 4. 正規化以便顯示
        disp_norm = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # 5. 顯示結果 (同時載入彩色影像用於對比)
        imgL_color = cv2.imread(self.base.imageL, cv2.IMREAD_COLOR)
        imgR_color = cv2.imread(self.base.imageR, cv2.IMREAD_COLOR)

        ImageWindow(imgL_color, "ImgL")
        ImageWindow(imgR_color, "ImgR")
        ImageWindow(disp_norm, "Disparity Map")
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()