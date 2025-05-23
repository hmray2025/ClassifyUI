import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QFileDialog, QMessageBox, QMenuBar, QAction
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
import os
import csv
import random
class ImageClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Classifier")
        self.setGeometry(50, 50, 1500, 800)
        # self.showFullScreen()

        self.image_dir_base = "./pics_NEW"
        self.image_dir = ""
        self.image_files = []
        self.orig_image_files = []
        self.current_index = -1
        self.classifications = {}
        self.previous_index = None
        self.total_count = 0
        self.timer = QTimer()
        self.time = 1200 # In seconds
        self.timer_running = False
        self.init_ui()

    def init_ui(self):
        # Menu bar
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        load_action = QAction("Load Images", self)
        load_action.triggered.connect(self.load_images)
        file_menu.addAction(load_action)

        quickload_action = QAction("Quick Load", self)
        quickload_action.triggered.connect(self.quickload_images)
        file_menu.addAction(quickload_action)

        save_action = QAction("Save Results", self)
        save_action.triggered.connect(self.save_results)
        file_menu.addAction(save_action)

        grade_action = QAction("Grade Results", self)
        grade_action.triggered.connect(self.grade_results)
        file_menu.addAction(grade_action)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Title section
        self.title_label = QLabel("Image Classifier")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 5px;")
        self.title_label.setFixedHeight(35)  # Adjust to 5% of a typical 600px window height

        # Main content section
        content_layout = QHBoxLayout()

        # Image display section
        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setFixedHeight(1500)

        # Sidebar section
        sidebar = QVBoxLayout()

        self.classify_yes_button = QPushButton("✔")
        self.classify_yes_button.setFixedSize(300, 100)
        # self.classify_yes_button.setStyleSheet("font-size: 24px; border: 1px solid green; background-color: white; border-radius: 5px")
        self.classify_yes_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                padding: 10px 20px;
                border: 1px solid black;
                border-radius: 5px;
                font-size: 40px
            }
            QPushButton:hover {
                background-color: #45a049; /* Darker green */
            }
            QPushButton:pressed {
                background-color: #3e8e41; /* Even darker green */
            }
        """)
        self.classify_yes_button.clicked.connect(lambda: self.classify_image(1))
        self.classify_yes_button.setEnabled(False)

        self.classify_no_button = QPushButton("✘")
        self.classify_no_button.setFixedSize(300, 100)
        # self.classify_no_button.setStyleSheet("font-size: 24px")
        self.classify_no_button.setStyleSheet("""
            QPushButton {
                background-color: #f05656;
                color: white;
                padding: 10px 20px;
                border: 1px solid black;
                border-radius: 5px;
                font-size: 40px
            }
            QPushButton:hover {
                background-color: #f23737;
            }
            QPushButton:pressed {
                background-color: #f21c1c;
            }
        """)
        self.classify_no_button.clicked.connect(lambda: self.classify_image(-1))
        self.classify_no_button.setEnabled(False)

        self.undo_button = QPushButton("Undo")
        self.undo_button.setFixedSize(300, 50)
        self.undo_button.setStyleSheet("font-size: 18px;")
        self.undo_button.clicked.connect(self.undo_classification)
        self.undo_button.setEnabled(False)

        self.instructions_label = QLabel("Is there a cone in this image?")
        self.instructions_label.setStyleSheet("font-size: 18px; padding-bottom: 60px")
        self.instructions_label.setAlignment(Qt.AlignCenter)

        self.classified_count_label = QLabel("Classified Images: 0")
        self.classified_count_label.setStyleSheet("font-size: 18px; padding-bottom: 30px")
        self.classified_count_label.setAlignment(Qt.AlignCenter)

        # Timer section
        self.timer_label = QLabel("20:00")
        self.timer_label.setStyleSheet("font-size: 24px; padding: 10px;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        
        timer_buttons_layout = QHBoxLayout()
        
        self.start_timer_button = QPushButton("Start")
        self.start_timer_button.setFixedSize(95, 30)
        self.start_timer_button.clicked.connect(self.start_timer)
        
        self.pause_timer_button = QPushButton("Pause")
        self.pause_timer_button.setFixedSize(95, 30)
        self.pause_timer_button.clicked.connect(self.pause_timer)
        self.pause_timer_button.setEnabled(False)
        
        self.stop_timer_button = QPushButton("Stop")
        self.stop_timer_button.setFixedSize(95, 30)
        self.stop_timer_button.clicked.connect(self.stop_timer)
        self.stop_timer_button.setEnabled(False)
        
        timer_buttons_layout.addWidget(self.start_timer_button)
        timer_buttons_layout.addWidget(self.pause_timer_button)
        timer_buttons_layout.addWidget(self.stop_timer_button)
        
        
        
        # Add existing instruction label and other components after this
        sidebar.addWidget(self.instructions_label)
        sidebar.addWidget(self.classified_count_label)
        sidebar.addWidget(self.classify_yes_button)
        sidebar.addWidget(self.classify_no_button)
        sidebar.addWidget(self.undo_button)

        # Add timer components to sidebar
        sidebar.addWidget(self.timer_label)
        sidebar.addLayout(timer_buttons_layout)

        # sidebar.setSpacing(10)
        # sidebar.setContentsMargins(10, 10, 10, 10)
        sidebar.setAlignment(Qt.AlignVCenter)

        # Setup Alignment
        content_layout.addWidget(self.image_label, 5)
        content_layout.addLayout(sidebar, 1)
        content_layout.setAlignment(Qt.AlignCenter)

        # content_layout.setStretch(0, 5)

        main_layout.addWidget(self.title_label)
        main_layout.addLayout(content_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def load_images(self, file):
        if file:
            self.image_dir = self.image_dir_base
        else:
            self.image_dir = QFileDialog.getExistingDirectory(self, "Select Image Directory")

        if self.image_dir:
            self.image_files = [f for f in os.listdir(self.image_dir) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]

            # Store the original order of images
            self.orig_image_files = self.image_files.copy()

            # Randomize the order of images
            random.shuffle(self.image_files)


            if not self.image_files:
                QMessageBox.warning(self, "No Images", "No image files found in the selected directory.")
                return

            self.classifications.clear()
            self.current_index = 0
            self.update_classified_count()
            self.display_image(0)
            self.classify_yes_button.setEnabled(True)
            self.classify_no_button.setEnabled(True)
            self.total_count = len(self.image_files)

    def quickload_images(self,):
        self.load_images(" ")

    def display_image(self, index):
        if 0 <= index < len(self.image_files):
            self.current_index = index
            image_path = os.path.join(self.image_dir, self.image_files[index])
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_label.clear()
            self.image_label.setText("No Image Loaded")

    def classify_image(self, classification):

        ## This is where we can randomize the image order
        if 0 <= self.current_index < len(self.image_files):
            file_name = self.image_files[self.current_index]
            self.classifications[file_name] = classification
            self.previous_index = self.current_index
            self.update_classified_count()

            # Automatically move to the next image
            if self.current_index + 1 < len(self.image_files):
                self.current_index += 1
                self.display_image(self.current_index)
                self.undo_button.setEnabled(True)
            else:
                self.classify_yes_button.setEnabled(False)
                self.classify_no_button.setEnabled(False)

    def undo_classification(self):
        if self.previous_index is not None:
            del self.classifications[self.image_files[self.previous_index]]
            self.current_index = self.previous_index
            self.previous_index = max(0, min(self.previous_index-1, self.total_count-2))
            self.display_image(self.current_index)
            self.update_classified_count()

        if self.current_index == 0:
            self.undo_button.setEnabled(False)

    def update_classified_count(self):
        classified_count = len(self.classifications)
        self.classified_count_label.setText(f"Classified Images: {classified_count}")

    def save_results(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "CSV Files (*.csv)")
        if save_path:
            try:
                with open(save_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Image", "Classification"])
                    for image, classification in self.classifications.items():
                        writer.writerow([image, classification])
                QMessageBox.information(self, "Success", "Classifications saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while saving results: {e}")

    def grade_results(self):
        correctAward = 0.05
        incorrectPenalty = 0.50
        if not self.image_dir:
            QMessageBox.warning(self, "No Directory Loaded", "Please load a directory first.")
            return

        truth_file_path = os.path.join(self.image_dir, "truth.csv")
        if not os.path.exists(truth_file_path):
            QMessageBox.warning(self, "Missing Truth File", "The truth.csv file is not found in the image directory.")
            return

        try:
            with open(truth_file_path, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                truth_data = {rows[0]: int(rows[1]) for rows in reader}
            ## This is where we can classify which images are correct
            ## and which are incorrect
            total = len(self.classifications.items())
            correct = sum(1 for image, classification in self.classifications.items() if truth_data.get(image) == classification)
            accuracy = (correct / total) * 100 if total > 0 else 0
            ## Round the total monies available to 2 decimal places and add a zero if it is less than 1
            ## This is to prevent the display of 0.5 as 0.50
            totalMonies = round(correctAward*correct-(total-correct)*incorrectPenalty, 2)
            if totalMonies < 0:
                totalMonies = 0.00
            totalMonies = "{:.2f}".format(totalMonies)
            QMessageBox.information(self, "Grading Results", f"Accuracy: {accuracy:.2f}%\
                                    \nCorrect: {correct}/{total}\
                                    \n Extra Money: ${totalMonies}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while grading results: {e}")

    def start_timer(self):
        if not self.timer_running:
            try:
                self.timer.timeout.disconnect()
            except TypeError:
                pass
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(1000)  # Update every second
            self.timer_running = True
            self.start_timer_button.setEnabled(False)
            self.pause_timer_button.setEnabled(True)
            self.stop_timer_button.setEnabled(True)
    
    def pause_timer(self):
        self.timer.stop()
        self.timer_running = False
        self.start_timer_button.setEnabled(True)
        self.pause_timer_button.setEnabled(False)
    
    def stop_timer(self):
        self.timer.stop()
        self.timer_running = False
        self.time = 1200  # Reset to 20 minutes
        minutes = (self.time % 3600) // 60
        seconds = self.time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.start_timer_button.setEnabled(True)
        self.pause_timer_button.setEnabled(False)
        self.stop_timer_button.setEnabled(False)
        self.timer_label.setStyleSheet("font-size: 24px; padding: 10px;")
    
    def update_timer(self):
        self.time -= 1
        minutes = (self.time % 3600) // 60
        seconds = self.time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        if self.time <= 300:
            self.timer_label.setStyleSheet("color: red; font-size: 24px; padding: 10px;")
        if self.time <= 0:
            self.stop_timer()
            QMessageBox.warning(self, "Time's Up!")

            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageClassifierApp()
    window.show()
    sys.exit(app.exec_())
