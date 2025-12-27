import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication

# 匯入我們新分離出來的邏輯處理器
from src.base_data import BaseData
from src.q1_handler import Q1_Handler
from src.q2_handler import Q2_Handler
from src.q3_handler import Q3_Handler
from src.q4_handler import Q4_Handler

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 載入 .ui 檔案
        # 確保 'MainWindow-cvdlhw1.ui' 和 main.py 在同一個資料夾
        uic.loadUi('MainWindow-cvdlhw1.ui', self) 
        
        # --- 1. 初始化共用資料 ---
        # 建立一個物件來儲存所有 Q (1, 2, 3) 都需要存取的圖片路徑
        self.base_data = BaseData(parent_window=self)

        # --- 2. 初始化所有邏輯處理器 ---
        # 將 'self' (主視窗) 和 'self.base_data' 傳遞給處理器
        # 這樣處理器就能存取 UI 元件 (例如 self.ui.extrinsicSpinBox)
        # 和共用資料 (例如 self.base.images)
        self.q1 = Q1_Handler(main_window=self, base_data=self.base_data)
        self.q2 = Q2_Handler(main_window=self, base_data=self.base_data)
        self.q3 = Q3_Handler(main_window=self, base_data=self.base_data)
        self.q4 = Q4_Handler(main_window=self) # Q4 有自己的讀圖按鈕，所以不用 base_data

        # --- 3. 連接所有按鈕訊號 ---
        
        # Load Image Group
        # 注意：我們將訊號連接到 base_data 物件的方法
        self.loadFolderButton.clicked.connect(self.base_data.load_folder)
        self.loadImageLButton.clicked.connect(self.base_data.load_imageL)
        self.loadImageRButton.clicked.connect(self.base_data.load_imageR)
        
        # 1. Calibration Group
        # 將 Q1 的按鈕連接到 q1 處理器的方法
        self.findCornersButton.clicked.connect(self.q1.find_corners)
        self.findIntrinsicButton.clicked.connect(self.q1.find_intrinsic)
        self.findExtrinsicButton.clicked.connect(self.q1.find_extrinsic)
        self.findDistortionButton.clicked.connect(self.q1.find_distortion)
        self.showResultButton.clicked.connect(self.q1.show_result)

        # 2. Augmented Reality Group
        self.showWordsOnBoardButton.clicked.connect(self.q2.show_on_board)
        self.showWordsVerticalButton.clicked.connect(self.q2.show_vertical)

        # 3. Stereo Disparity Map Group
        self.stereoDisparityMapButton.clicked.connect(self.q3.stereo_disparity)

        # 4. SIFT Group
        # Q4 的按鈕連接到 q4 處理器的方法
        self.loadSiftImage1Button.clicked.connect(self.q4.load_image1)
        self.loadSiftImage2Button.clicked.connect(self.q4.load_image2)
        self.keypointsButton.clicked.connect(self.q4.get_keypoints)
        self.matchedKeypointsButton.clicked.connect(self.q4.matched_keypoint)
        
        self.show()
        print("UI 載入完成, 等待操作...")

# --- 程式進入點 ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())