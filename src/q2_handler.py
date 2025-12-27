import cv2
import numpy as np
import os
from PyQt5.QtWidgets import QMessageBox

class Q2_Handler:
    def __init__(self, main_window, base_data):
        # 儲存對主視窗 UI 的參考
        self.ui = main_window 
        # 儲存對共用資料的參考
        self.base = base_data 
        
        # Q2 自己的內部狀態變數 (用於快取校準結果)
        self.ImagePoints = []
        self.ObjectPoints = []
        self.mat_intri = None
        self.cof_dist = None
        self.v_rot = None
        self.v_trans = None

    def _calibrate_q2_images(self):
        """
        為 Q2 執行獨立的相機校準。
        根據 PDF，Q2 使用 5 張影像 (1-5.bmp)。
        """
        # 檢查是否已校準
        if self.mat_intri is not None:
            return True

        self.ImagePoints.clear()
        self.ObjectPoints.clear()
        
        width, height = 11, 8
        objpoint=np.zeros((width*height,3),np.float32)
        objpoint[:,:2]=np.mgrid[0:width,0:height].T.reshape(-1, 2)
        
        # 從 base_data 獲取圖片路徑，並只取前 5 張
        q2_image_paths = self.base.images[:5]
        
        if len(q2_image_paths) < 5:
            QMessageBox.warning(self.ui, "Warning", f"Q2 requires at least 5 images in the loaded folder. Found {len(q2_image_paths)}.")
            return False
            
        print(f"Calibrating for Q2 using {len(q2_image_paths)} images...")

        for image_path in q2_image_paths:
            img = cv2.imread(image_path)
            if img is None:
                print(f"Warning: Could not read {image_path}")
                continue
            grayimg=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            ret,corners=cv2.findChessboardCorners(grayimg, (width, height), None)

            if ret:
                self.ImagePoints.append(corners)
                self.ObjectPoints.append(objpoint)
        
        if not self.ObjectPoints:
            QMessageBox.critical(self.ui, "Error", "No corners found in Q2 images (1-5.bmp). Cannot calibrate.")
            return False

        # 根據 PDF，影像大小為 2048x2048
        ret, self.mat_intri, self.cof_dist, self.v_rot, self.v_trans = cv2.calibrateCamera (self.ObjectPoints, self.ImagePoints, (2048, 2048) ,None, None)
        
        if ret:
            # print("Q2 Calibration successful.")
            return True
        else:
            QMessageBox.critical(self.ui, "Error", "Q2 Calibration failed.")
            return False

    def _run_ar(self, vertical: bool):
        # 1. 確保已校準
        if not self._calibrate_q2_images():
            print("Cannot run AR without calibration.")
            return

        # 2. 獲取 UI 文字
        # *** 關鍵點：從 self.ui 存取 UI 元件 ***
        text = self.ui.arTextBox.text()
        
        if not text:
            QMessageBox.warning(self.ui, "Warning", "Please enter text in the box.")
            return
        if len(text) > 6:
            QMessageBox.warning(self.ui, "Warning", "Text must be 6 characters or less.")
            text = text[:6] # 截斷

        # 3. 準備資料庫
        offsets =[[7.0, 5.0, 0.0], [4.0, 5.0, 0.0], [1.0, 5.0, 0.0], [7.0, 2.0, 0.0], [4.0, 2.0, 0.0], [1.0, 2.0, 0.0]]
        
        if vertical:
            db_name = 'alphabet_db_vertical.txt'
        else:
            db_name = 'alphabet_db_onboard.txt'
            
        # 假設資料庫在 Q2_Image 資料夾下的 Q2_db 資料夾中
        db_path = os.path.join(self.base.folder_path, "Q2_db", db_name)
        
        if not os.path.exists(db_path):
            QMessageBox.critical(self.ui, "Error", f"Database file not found. Expected at: {db_path}")
            return
            
        fs = cv2.FileStorage(db_path, cv2.FILE_STORAGE_READ)
        if not fs.isOpened():
            QMessageBox.critical(self.ui, "Error", f"Failed to open database file: {db_path}")
            return

        # 4. 迭代影像並繪製
        q2_image_paths = self.base.images[:5]
        for j in range(len(q2_image_paths)):
            img = cv2.imread(q2_image_paths[j])
            
            for i in range(len(text)):
                ch_mat = fs.getNode(text[i].upper()).mat() # 轉大寫
                if ch_mat is None:
                    print(f"Character '{text[i]}' not found in db.")
                    continue
                    
                ch_mat=np.float32(ch_mat).reshape(-1,3)
                ch_mat_offset = ch_mat + offsets[i] # 應用平移
                
                # 投影到 2D 影像
                img_points, jac = cv2.projectPoints(ch_mat_offset, self.v_rot[j], self.v_trans[j], self.mat_intri, self.cof_dist)
                
                # 繪製線條
                for k in range(len(img_points)//2):
                    pt1=tuple(map(int,img_points[2*k].ravel()))
                    pt2=tuple(map(int,img_points[2*k+1].ravel()))
                    img = cv2.line(img, pt1, pt2, (0, 0, 255), 5) # 畫紅線
                        
            img=cv2.resize(img,(1000,800))
            cv2.imshow(f'AR {j+1}.bmp',img)
            cv2.waitKey(1200)
            cv2.destroyAllWindows()
        
        fs.release()

    def show_on_board(self):
        print("=2.1 Show Words on Board")
        self._run_ar(vertical=False)

    def show_vertical(self):
        print("=2.2 Show Words Vertical")
        self._run_ar(vertical=True)