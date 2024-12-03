import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox, QGroupBox, QFormLayout, QDialog
)
from PyQt5.QtCore import Qt


class SQLParserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parser SQL")
        self.setGeometry(300, 300, 600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.sql_input = QLineEdit()
        self.sql_input.setPlaceholderText("Escribe la consulta SQL aquí")
        layout.addWidget(QLabel("Consulta SQL:"))
        layout.addWidget(self.sql_input)

        self.parse_button = QPushButton("Parsear y Ejecutar")
        self.parse_button.clicked.connect(self.parse_and_execute)
        layout.addWidget(self.parse_button)

        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)

        self.result_label = QLabel("Resultados aparecerán aquí.")
        layout.addWidget(self.result_label)
        
        self.result_label = QLabel(self) 
        self.setLayout(layout)

    def parse_and_execute(self):
        sql_query = self.sql_input.text()
        if not sql_query.strip():
            self.result_label.setText("Por favor, ingrese una consulta SQL válida.")
            return

        try:
            parsed_query = self.parse_sql_query(sql_query)
            if not parsed_query:
                self.result_label.setText("Consulta SQL no válida o no soportada.")
                return

            payload = {
                "database": "postgreSQL",
                "query": parsed_query["query"],
                "K": parsed_query["K"]
            }
            url = "http://127.0.0.1:8000/database/query"

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            self.display_results(data["result"], data["time"])

        except Exception as e:
            self.result_label.setText(f"Error: {e}")

    def parse_sql_query(self, sql_query):
        import re

        match = re.match(
            r"SELECT \* FROM wines WHERE description @@\('(.+)'\) LIMIT (\d+);", sql_query, re.IGNORECASE
        )
        if match:
            keywords = match.group(1).replace("&", "").split()
            k_value = int(match.group(2))
            return {"query": " ".join(keywords), "K": k_value}
        return None

    def display_results(self, results, elapsed_time):
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Title", "Country", "Description", "Designation", "Points", "Price",
            "Province", "Region 1", "Region 2", "Taster Name", "Taster Twitter", "Variety", "Winery"
        ])
        
        for row_num, row_data in enumerate(results):
            self.results_table.insertRow(row_num)
            self.results_table.setItem(row_num, 0, QTableWidgetItem(str(row_data.get("id", ""))))
            self.results_table.setItem(row_num, 1, QTableWidgetItem(row_data.get("country", "")))
            self.results_table.setItem(row_num, 2, QTableWidgetItem(row_data.get("description", "")))
            self.results_table.setItem(row_num, 3, QTableWidgetItem(row_data.get("designation", "")))
            self.results_table.setItem(row_num, 4, QTableWidgetItem(str(row_data.get("points", ""))))
            self.results_table.setItem(row_num, 5, QTableWidgetItem(str(row_data.get("price", ""))))
            self.results_table.setItem(row_num, 6, QTableWidgetItem(row_data.get("province", "")))
            self.results_table.setItem(row_num, 7, QTableWidgetItem(row_data.get("region_1", "")))
            self.results_table.setItem(row_num, 8, QTableWidgetItem(row_data.get("region_2", "")))
            self.results_table.setItem(row_num, 9, QTableWidgetItem(row_data.get("taster_name", "")))
            self.results_table.setItem(row_num, 10, QTableWidgetItem(row_data.get("taster_twitter_handle", "")))
            self.results_table.setItem(row_num, 11, QTableWidgetItem(row_data.get("title", "")))
            self.results_table.setItem(row_num, 12, QTableWidgetItem(row_data.get("variety", "")))
            self.results_table.setItem(row_num, 13, QTableWidgetItem(row_data.get("winery", "")))

        self.result_label.setText(f"Búsqueda completada en {elapsed_time:.2f} segundos.")


class SearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Índice Invertido - Buscador")
        self.setGeometry(200, 200, 800, 600)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        input_group = QGroupBox("Búsqueda por Consulta")
        input_layout = QFormLayout()

        self.database_select = QComboBox()
        self.database_select.addItems(["postgreSQL", "Propia"])
        input_layout.addRow(QLabel("Base de Datos:"), self.database_select)

        self.query_input = QLineEdit()
        input_layout.addRow(QLabel("Consulta (Query):"), self.query_input)
        
        self.k_input = QSpinBox()
        self.k_input.setMinimum(1)
        self.k_input.setMaximum(100)
        self.k_input.setValue(10)
        input_layout.addRow(QLabel("Top K:"), self.k_input)

        self.search_button = QPushButton("Buscar por Query")
        self.search_button.clicked.connect(self.perform_query_search)
        input_layout.addRow(self.search_button)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        docid_group = QGroupBox("Búsqueda por DocID")
        docid_layout = QFormLayout()

        self.docid_input = QLineEdit()
        docid_layout.addRow(QLabel("DocID:"), self.docid_input)

        self.docid_search_button = QPushButton("Buscar por DocID")
        self.docid_search_button.clicked.connect(self.perform_docid_search)
        docid_layout.addRow(self.docid_search_button)

        docid_group.setLayout(docid_layout)
        main_layout.addWidget(docid_group)

        self.segundos = 0
        self.label_display = QLabel("El query fue ejecutado en "+ str(self.segundos) + " segundos.")
        self.label_display.setAlignment(Qt.AlignCenter)  # Centrar el texto
        main_layout.addWidget(self.label_display)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(14)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Title", "Country", "Description", "Designation", "Points", "Price",
            "Province", "Region 1", "Region 2", "Taster Name", "Taster Twitter", "Variety", "Winery"
        ])
        main_layout.addWidget(self.results_table)

        self.sql_parser_button = QPushButton("Abrir Parser SQL")
        self.sql_parser_button.clicked.connect(self.open_sql_parser)
        main_layout.addWidget(self.sql_parser_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def perform_query_search(self):
        database = self.database_select.currentText()
        query = self.query_input.text()
        k = self.k_input.value()

        if not query:
            return

        url = "http://127.0.0.1:8000/database/query"
        payload = {"database": database, "query": query, "K": k}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            self.display_query_results(data["result"], data["time"])
        except Exception as e:
            print(f"Error: {e}")

    def perform_docid_search(self):
        docid = self.docid_input.text()

        if not docid:
            return

        url = "http://127.0.0.1:8000/docID"
        payload = {"docId": int(docid)}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            self.display_docid_results(data)
        except Exception as e:
            print(f"Error: {e}")

    def display_query_results(self, results, elapsed_time):
        self.results_table.setRowCount(0)

        for row_data in results:
            row_num = self.results_table.rowCount()
            self.results_table.insertRow(row_num)

            self.results_table.setItem(row_num, 0, QTableWidgetItem(str(row_data[0])))
            self.results_table.setItem(row_num, 1, QTableWidgetItem(row_data[1]))
            self.results_table.setItem(row_num, 2, QTableWidgetItem(str(row_data[2])))

        self.segundos = elapsed_time
        self.label_display.setText(f"Búsqueda completada en {elapsed_time:.2f} segundos.")

    def display_docid_results(self, data):
        self.results_table.setRowCount(0)

        row_num = self.results_table.rowCount()
        self.results_table.insertRow(row_num)

        self.results_table.setItem(row_num, 0, QTableWidgetItem(str(data.get("id", ""))))
        self.results_table.setItem(row_num, 1, QTableWidgetItem(data.get("title", "")))
        self.results_table.setItem(row_num, 2, QTableWidgetItem(data.get("country", "")))
        self.results_table.setItem(row_num, 3, QTableWidgetItem(data.get("description", "")))
        self.results_table.setItem(row_num, 4, QTableWidgetItem(data.get("designation", "")))
        self.results_table.setItem(row_num, 5, QTableWidgetItem(str(data.get("points", ""))))
        self.results_table.setItem(row_num, 6, QTableWidgetItem(str(data.get("price", ""))))
        self.results_table.setItem(row_num, 7, QTableWidgetItem(data.get("province", "")))
        self.results_table.setItem(row_num, 8, QTableWidgetItem(data.get("region_1", "")))
        self.results_table.setItem(row_num, 9, QTableWidgetItem(data.get("region_2", "")))
        self.results_table.setItem(row_num, 10, QTableWidgetItem(data.get("taster_name", "")))
        self.results_table.setItem(row_num, 11, QTableWidgetItem(data.get("taster_twitter_handle", "")))
        self.results_table.setItem(row_num, 12, QTableWidgetItem(data.get("variety", "")))
        self.results_table.setItem(row_num, 13, QTableWidgetItem(data.get("winery", "")))


    def open_sql_parser(self):
        self.sql_parser_dialog = SQLParserDialog()
        self.sql_parser_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchApp()
    window.show()
    sys.exit(app.exec_())