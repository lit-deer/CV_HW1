import glob
from PyQt5.QtWidgets import QFileDialog
import os

class BaseData:
    def __init__(self, parent_window):
        # 需要 'parent_window' 才能彈出 QFileDialog
        self.parent = parent_window 
        
        # 儲存圖片路徑的變數
        self.images = []       # Q1, Q2 使用
        self.folder_path = ""  # Q1, Q2 使用
        self.imageL = None     # Q3 使用
        self.imageR = None     # Q3 使用

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self.parent, "Select Folder Containing Images")
        if folder_path:
            # 儲存 .bmp 圖片路徑
            image_paths = glob.glob(folder_path + "/*.bmp")
            self.images = sorted(image_paths, key=lambda path: int(os.path.splitext(os.path.basename(path))[0]))
            self.folder_path = folder_path
            print(f"Loaded folder: {folder_path}")
            print(f"Found {len(self.images)} .bmp files.")

    def load_imageL(self):
        # 載入左影像
        file_name, _ = QFileDialog.getOpenFileName(self.parent, "Open Image File", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)")
        if file_name:
            self.imageL = file_name
            print(f"Loaded Image_L: {file_name}")

    def load_imageR(self):
        # 載入右影像
        file_name, _ = QFileDialog.getOpenFileName(self.parent, "Open Image File", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)")
        if file_name:
            self.imageR = file_name
            print(f"Loaded Image_R: {file_name}")