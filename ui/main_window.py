import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QTextEdit,
                             QHBoxLayout, QHeaderView)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Message Editor")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Commit history table
        self.commit_table = QTableWidget()
        self.commit_table.setColumnCount(3)
        self.commit_table.setHorizontalHeaderLabels(["SHA", "Author", "Message"])
        self.commit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.commit_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.commit_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        main_layout.addWidget(self.commit_table)

        # Commit message editor
        self.commit_message_edit = QTextEdit()
        main_layout.addWidget(self.commit_message_edit)

        # Buttons
        button_layout = QHBoxLayout()
        self.amend_button = QPushButton("Amend Commit Message")
        self.revert_button = QPushButton("Revert Commit")
        button_layout.addWidget(self.amend_button)
        button_layout.addWidget(self.revert_button)
        main_layout.addLayout(button_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
