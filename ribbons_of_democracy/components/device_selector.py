from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class DeviceSelector(QDialog):
    def __init__(self, parent, available_devices):
        super().__init__(parent)
        self.setWindowTitle("Select Device")
        self.setModal(True)
        self.selected_device = None

        layout = QVBoxLayout(self)
        
        self.device_list = QListWidget()
        for device in available_devices:
            item = QListWidgetItem(device['name'])
            item.setIcon(QIcon(device['path']))
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)
        
        layout.addWidget(self.device_list)

        button_layout = QHBoxLayout()
        select_button = QPushButton("Select")
        select_button.clicked.connect(self.select_device)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def select_device(self):
        current_item = self.device_list.currentItem()
        if current_item:
            self.selected_device = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
