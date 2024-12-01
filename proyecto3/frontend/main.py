import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QComboBox, QLineEdit, QWidget, QScrollArea, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
import json
import urllib.parse

class KNNApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto 3")
        self.setGeometry(100, 100, 800, 600)

        self.main_layout = QVBoxLayout()
        self.initUI()

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def initUI(self):
        self.insert_label = QLabel("Insertar Imagen")
        self.main_layout.addWidget(self.insert_label)

        self.insert_button = QPushButton("Elige una imagen para insertar")
        self.insert_button.clicked.connect(self.insert_image)
        self.main_layout.addWidget(self.insert_button)

        self.insert_preview = QLabel("Preview")
        self.insert_preview.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.insert_preview)

        # Search section
        self.search_label = QLabel("Search Nearest Images")
        self.main_layout.addWidget(self.search_label)

        # Search Method
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Sequential (KNN)", "R-tree", "Faiss"])
        self.main_layout.addWidget(self.method_combo)

        # k or Radius Input
        self.k_input = QLineEdit()
        self.k_input.setPlaceholderText("Enter K or R (for range search)")
        self.main_layout.addWidget(self.k_input)

        self.search_button = QPushButton("Image for Search")
        self.search_button.clicked.connect(self.search_images)
        self.main_layout.addWidget(self.search_button)

        self.results_area = QScrollArea()
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_widget.setLayout(self.results_layout)
        self.results_area.setWidget(self.results_widget)
        self.main_layout.addWidget(self.results_area)

    def insert_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image")
        if image_path:
            encoded_path = urllib.parse.quote(image_path)
            method = self.method_combo.currentText()

            # Mapa
            url_map = {
                "Sequential (k-NN)": "/insert_image_sequential/",
                "R-tree": "/insert_image_rtree/",
                "Faiss": "/insert_image_high_d/"
            }
            url = url_map.get(method)
            full_url = f"http://127.0.0.1:8000{url}?image_path={encoded_path}"

            try:
                response = requests.post(full_url, headers={'accept': 'application/json'})

                if response.status_code == 200:
                    result = response.json()
                    self.insert_preview.setPixmap(QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio))
                    QMessageBox.information(self, "Success", result.get("message", "Inserted successfully"))
                else:
                    QMessageBox.critical(self, "Error", f"Failed to insert image: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error occurred: {str(e)}")


    def search_images(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Query Image")
        if not image_path:
            return

        method = self.method_combo.currentText()
        k_or_radius = self.k_input.text()

        endpoint_map = {
            "Sequential (k-NN)": "knn_search_sequential/",
            "R-tree": "knn_search_rtree/",
            "Faiss": "knn_search_high_d/"
        }
        endpoint = endpoint_map.get(method)

        if "Sequential" in method and not k_or_radius.isdigit():
            endpoint = "range_search_sequential/"
            data = {"query_image_path": image_path, "radius": float(k_or_radius)}
        else:
            data = {"query_image_path": image_path, "k": int(k_or_radius)}

        response = requests.post(f"http://127.0.0.1:8000/{endpoint}", json=data)
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success":
                self.display_results(result.get("results", []))
            else:
                QMessageBox.warning(self, "Warning", result.get("message", "No results found."))
        else:
            QMessageBox.critical(self, "Error", f"Search request failed: {response.text}")

    def display_results(self, image_paths):
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for img_path in image_paths:
            label = QLabel()
            pixmap = QPixmap(img_path)
            label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
            self.results_layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KNNApp()
    window.show()
    sys.exit(app.exec_())
