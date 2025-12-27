import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from src.ui_util import ImageWindow # 您可以保留 ui_util.py 來放 ImageWindow

class Q4_Handler:
    def __init__(self, main_window):
        # 儲存對主視窗 UI 的參考
        self.ui = main_window 
        
        # Q4 自己的內部狀態變數
        self.image1 = None
        self.image2 = None
        self.keypoints1 = None
        self.descriptors1 = None
        self.keypoints2 = None
        self.descriptors2 = None

    def load_image1(self):
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Image File", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)")
        if file_name:
            self.image1 = cv2.imread(file_name)
            self.keypoints1 = None
            self.descriptors1 = None
            print("Loaded Q4 Image 1")

    def load_image2(self):
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Image File", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)")
        if file_name:
            self.image2 = cv2.imread(file_name)
            self.keypoints2 = None
            self.descriptors2 = None
            print("Loaded Q4 Image 2")

    def get_keypoints(self):
        if self.image1 is None:
            QMessageBox.warning(self.ui, "Warning", "Please load Image 1 first")
            return

        gray = cv2.cvtColor(self.image1, cv2.COLOR_BGR2GRAY)
        sift = cv2.SIFT_create()
        self.keypoints1, self.descriptors1 = sift.detectAndCompute(gray, None)
        img_with_keypoints = cv2.drawKeypoints(gray, self.keypoints1, None, color=(0, 255, 0))
        print("=4.1 Keypoints")
        ImageWindow(img_with_keypoints, "4.1 Keypoints") # 使用輔助類別
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def matched_keypoint(self):
        if self.image1 is None or self.image2 is None:
            QMessageBox.warning(self.ui, "Warning", "Please load both images first")
            return
            
        try:
            if self.keypoints1 is None:
                gray1 = cv2.cvtColor(self.image1, cv2.COLOR_BGR2GRAY)
                sift1 = cv2.SIFT_create()
                self.keypoints1, self.descriptors1 = sift1.detectAndCompute(gray1, None)
            
            if self.keypoints2 is None:
                gray2 = cv2.cvtColor(self.image2, cv2.COLOR_BGR2GRAY)
                sift2 = cv2.SIFT_create()
                self.keypoints2, self.descriptors2 = sift2.detectAndCompute(gray2, None)

            if self.descriptors1 is None or self.descriptors2 is None:
                print("Could not compute descriptors.")
                return

            bf = cv2.BFMatcher()
            matches = bf.knnMatch(self.descriptors1, self.descriptors2, k=2)
            
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append([m]) 

            img_matches = cv2.drawMatchesKnn(self.image1, self.keypoints1, 
                                             self.image2, self.keypoints2, 
                                             good_matches, None, 
                                             flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            print("=4.2 Matched Keypoints")
            ImageWindow(img_matches, "4.2 Matched Keypoints")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"An error occurred: {e}")