from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QStackedWidget)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QFont, QImage
import cv2
from PIL import Image
from datetime import datetime
import sys
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SeniOS")
        self.setMinimumSize(800, 600)

        # Hauptwidget und Layout erstellen
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.home_page = self.create_home_page()
        self.video_page = self.create_video_page()
        self.photo_page = self.create_photo_page()
        self.cards_page = self.create_cards_page()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.video_page)
        self.stacked_widget.addWidget(self.photo_page)
        self.stacked_widget.addWidget(self.cards_page)
        
        self.main_layout.addWidget(self.stacked_widget)

        # Video playback properties
        self.video_capture = None
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_frame)
        self.is_playing = False

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Willkommens-Label
        welcome_label = QLabel("Willkommen zu SeniOS!")
        welcome_label.setStyleSheet("font-size: 24px; margin: 20px;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Create button layout
        button_layout = QVBoxLayout()
        
        # Create main menu buttons
        video_btn = self.create_menu_button("Videos anschauen", lambda: self.stacked_widget.setCurrentIndex(1))
        photo_btn = self.create_menu_button("Fotos ansehen", lambda: self.stacked_widget.setCurrentIndex(2))
        cards_btn = self.create_menu_button("Karten erstellen", lambda: self.stacked_widget.setCurrentIndex(3))
        
        button_layout.addWidget(video_btn)
        button_layout.addWidget(photo_btn)
        button_layout.addWidget(cards_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Zeit-Label
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 18px;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_time()
        layout.addWidget(self.time_label)
        
        return page

    def create_video_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Videos")
        title.setStyleSheet("font-size: 24px; margin: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Video display label
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label)
        
        # Video controls
        controls_layout = QHBoxLayout()
        self.play_pause_btn = self.create_menu_button("Abspielen/Pause", self.toggle_video)
        select_btn = self.create_menu_button("Video auswählen", self.open_video)
        back_btn = self.create_menu_button("Zurück", self.stop_and_go_home)
        
        controls_layout.addWidget(select_btn)
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(back_btn)
        layout.addLayout(controls_layout)
        
        return page

    def create_photo_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Fotos")
        title.setStyleSheet("font-size: 24px; margin: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.photo_label)
        
        button_layout = QHBoxLayout()
        select_btn = self.create_menu_button("Foto auswählen", self.open_photo)
        back_btn = self.create_menu_button("Zurück", lambda: self.stacked_widget.setCurrentIndex(0))
        
        button_layout.addWidget(select_btn)
        button_layout.addWidget(back_btn)
        layout.addLayout(button_layout)
        
        return page

    def create_cards_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Karten erstellen")
        title.setStyleSheet("font-size: 24px; margin: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add card creation widgets here
        button_layout = QHBoxLayout()
        create_btn = self.create_menu_button("Neue Karte", self.create_new_card)
        back_btn = self.create_menu_button("Zurück", lambda: self.stacked_widget.setCurrentIndex(0))
        
        button_layout.addWidget(create_btn)
        button_layout.addWidget(back_btn)
        layout.addLayout(button_layout)
        
        return page

    def create_menu_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                padding: 15px;
                margin: 10px;
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button.clicked.connect(callback)
        return button

    def open_video(self):
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_timer.stop()
            self.is_playing = False
            
        file_name, _ = QFileDialog.getOpenFileName(self, "Video auswählen", "", 
            "Video Files (*.mp4 *.avi *.mkv)")
        if file_name:
            self.video_capture = cv2.VideoCapture(file_name)
            if self.video_capture.isOpened():
                self.toggle_video()

    def toggle_video(self):
        if self.video_capture is None:
            return
            
        if self.is_playing:
            self.video_timer.stop()
            self.is_playing = False
            self.play_pause_btn.setText("Abspielen")
        else:
            self.video_timer.start(33)  # ~30 fps
            self.is_playing = True
            self.play_pause_btn.setText("Pause")

    def update_video_frame(self):
        if self.video_capture is None:
            return
            
        ret, frame = self.video_capture.read()
        if ret:
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            
            # Convert to QImage
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Scale to fit the label while maintaining aspect ratio
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.video_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)
        else:
            self.video_timer.stop()
            self.is_playing = False
            self.play_pause_btn.setText("Abspielen")
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def stop_and_go_home(self):
        if self.video_capture is not None:
            self.video_timer.stop()
            self.video_capture.release()
            self.video_capture = None
            self.is_playing = False
        self.stacked_widget.setCurrentIndex(0)

    def open_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Foto auswählen", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(self.photo_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation)
            self.photo_label.setPixmap(scaled_pixmap)

    def create_new_card(self):
        # Basic card creation functionality - can be expanded
        file_name, _ = QFileDialog.getSaveFileName(self, "Karte speichern", "", 
            "Image Files (*.png *.jpg)")
        if file_name:
            # Create a basic card with PIL
            img = Image.new('RGB', (800, 600), color='white')
            img.save(file_name)

    def update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.setText(f'Aktuelle Zeit: {current_time}')

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont()
    font.setPointSize(12)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()