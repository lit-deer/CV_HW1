import cv2
import numpy as np
import os
from PyQt5.QtWidgets import QMessageBox

class Q1_Handler:
    def __init__(self, main_window, base_data):
        # 儲存對主視窗 UI 的參考
        self.ui = main_window 
        # 儲存對共用資料的參考
        self.base = base_data 
        
        # Q1 自己的內部狀態變數
        self.ObjectPoints = []
        self.ImagePoints = []
        self.mat_intri = None
        self.cof_dist = None
        self.v_rot = None
        self.v_trans = None

    def find_corners(self):
        self.ImagePoints.clear()
        self.ObjectPoints.clear()
        
        width, height = 11, 8
        objpoint=np.zeros((width*height,3),np.float32)
        objpoint[:,:2]=np.mgrid[0:width,0:height].T.reshape(-1, 2)
        
        # 從 base_data 獲取圖片路徑
        images_paths = self.base.images
        if not images_paths:
            QMessageBox.warning(self.ui, "Warning", "Please load folder first.")
            return
        print("=1.1 Corner detection")
        print(f"Finding corners in {len(images_paths)} images...")
        for image_path in images_paths:
            img = cv2.imread(image_path)
            grayimg=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            ret,corners=cv2.findChessboardCorners(grayimg, (width, height), None)

            if ret:
                winSize = (5, 5)
                zeroZone = (-1, -1)
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                cv2.cornerSubPix(grayimg, corners, winSize, zeroZone, criteria)
                
                self.ImagePoints.append(corners)
                self.ObjectPoints.append(objpoint)
                
                img_draw=cv2.cvtColor(grayimg,cv2.COLOR_GRAY2RGB)
                cv2.drawChessboardCorners(img_draw, (width, height), corners, ret)
                img_draw=cv2.resize(img_draw,(1000,800))
                cv2.imshow(os.path.basename(image_path), img_draw)
                cv2.waitKey(900)
                cv2.destroyAllWindows()
        print("Corner detection finished.")

    def find_intrinsic(self):
        if not self.ObjectPoints:
            QMessageBox.warning(self.ui, "Warning", "Please run 1.1 Find Corners first.")
            return
            
        width, height = 11, 8 
        img_size = (2048, 2048) # 根據 PDF
        
        ret, ins, cof_dist, v_rot, v_trans = cv2.calibrateCamera (self.ObjectPoints, self.ImagePoints, img_size ,None, None)
        
        self.mat_intri = ins
        self.cof_dist = cof_dist
        self.v_rot = v_rot
        self.v_trans = v_trans

        if ret:
            print("=1.2 Intrinsic:", ins)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(np.array2string(ins))
            msg.setWindowTitle("Intrinsic")
            msg.exec_()

    def find_extrinsic(self):
        if self.mat_intri is None:
            QMessageBox.warning(self.ui, "Warning", "Please run 1.2 Find Intrinsic first.")
            return

        # *** 關鍵點：從 self.ui 存取 UI 元件 ***
        num = self.ui.extrinsicSpinBox.value() - 1 
        
        if num >= len(self.v_rot) or num < 0:
            print(f"Invalid image index {num+1}.")
            return

        rvec = self.v_rot[num]
        tvec = self.v_trans[num]
        
        Rotation_matrix,_=cv2.Rodrigues(rvec)
        Extrinsic_matrix=np.column_stack((Rotation_matrix,tvec))
        
        print(f'=1.3 Extrinsic {num+1}.bmp:')
        print(Extrinsic_matrix)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(np.array2string(Extrinsic_matrix))
        msg.setWindowTitle(f'Extrinsic {num+1}.bmp:')
        msg.exec_()

    def find_distortion(self):
        if self.cof_dist is None:
            QMessageBox.warning(self.ui, "Warning", "Please run 1.2 Find Intrinsic first.")
            return
            
        print("=1.4 Distortion:")
        print(self.cof_dist)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(np.array2string(self.cof_dist))
        msg.setWindowTitle(f'Distortion:')
        msg.exec_()

    def show_result(self):
        # 1. 檢查校準是否完成
        if self.mat_intri is None or self.cof_dist is None:
            QMessageBox.warning(self.ui, "Warning", "Please run 1.2 Find Intrinsic first.")
            return
        print("=1.5 Show result") 
        # 2. 獲取 SpinBox 的當前值 (1-based index)
        try:
            selected_index = self.ui.extrinsicSpinBox.value() - 1 # 轉成 0-based index
        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Cannot access UI component 'extrinsicSpinBox': {e}")
            return
            
        # 3. 檢查索引是否有效
        if not (0 <= selected_index < len(self.base.images)):
            QMessageBox.warning(self.ui, "Warning", f"Selected index {selected_index+1} is out of range (Total images: {len(self.base.images)}).")
            return
            
        # 4. 獲取單一影像路徑 (移除 for 迴圈)
        img_path = self.base.images[selected_index]
        
        img = cv2.imread(img_path)
        if img is None:
            QMessageBox.critical(self.ui, "Error", f"Failed to read image: {img_path}")
            return
            
        # 5. 執行校正
        undistorted_img = cv2.undistort(img, self.mat_intri, self.cof_dist)
        
        # 6. 加上文字
        cv2.putText(img, 'Distorted', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 10)
        cv2.putText(undistorted_img, 'Undistorted', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 10)

        # 7. 組合影像
        concatenated_img = np.hstack([img, undistorted_img])
        concatenated_img = cv2.resize(concatenated_img, (1500, 800))
        
        # 8. 顯示單一結果
        win_name = f'{os.path.basename(img_path)} - Distorted (left) vs Undistorted (right)'
        cv2.imshow(win_name, concatenated_img)
        cv2.waitKey(0) # 改成 0，無限等待，直到使用者按下按鍵
        cv2.destroyAllWindows()
    # def show_result(self):
    #     if self.mat_intri is None or self.cof_dist is None:
    #         QMessageBox.warning(self.ui, "Warning", "Please run 1.2 Find Intrinsic first.")
    #         return
    #     print("=1.5 Show result")
    #     for i in range(len(self.base.images)):
    #         img_path = self.base.images[i]
    #         img = cv2.imread(img_path)
    #         if img is None:
    #             continue
                
    #         undistorted_img=cv2.undistort(img, self.mat_intri, self.cof_dist)
            
    #         cv2.putText(img, 'Distorted', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 10)
    #         cv2.putText(undistorted_img, 'Undistorted', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 10)

    #         concatenated_img=np.hstack([img,undistorted_img])
    #         concatenated_img=cv2.resize(concatenated_img,(1500,800))
            
    #         win_name = f'{os.path.basename(img_path)} - Distorted (left) vs Undistorted (right)'
    #         cv2.imshow(win_name, concatenated_img)
    #         cv2.waitKey(1200)
    #         cv2.destroyAllWindows()