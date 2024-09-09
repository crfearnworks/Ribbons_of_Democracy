from PyQt6.QtWidgets import QInputDialog, QColorDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from .ribbon_drawer import RIBBON_WIDTH, RIBBON_HEIGHT

def get_stripe_input(parent, default_x=0, default_width=50, default_color=None):
    dialog = StripeDialog(parent, default_x, default_width, default_color)
    if dialog.exec():
        x, width, color = dialog.get_values()
        return x, width, color.name()
    return None

def get_device_input(parent, default_name="", default_x=0, default_y=50):
    name, ok = QInputDialog.getText(parent, "Add Device", "Enter device name:", text=default_name)
    if ok and name:
        color = QColorDialog.getColor()
        if color.isValid():
            x, ok1 = QInputDialog.getInt(parent, "Device Position", "Enter X coordinate:", default_x, 0, RIBBON_WIDTH)
            y, ok2 = QInputDialog.getInt(parent, "Device Position", "Enter Y coordinate:", default_y, 0, RIBBON_HEIGHT)
            if ok1 and ok2:
                return name, color.name(), x, y
    return None

def select_item(parent, title, prompt, items):
    if not items:
        QMessageBox.information(parent, title, f"No {title.lower()} to select.")
        return None
    item, ok = QInputDialog.getItem(parent, title, prompt, items, 0, False)
    if ok and item:
        return items.index(item)
    return None

class StripeDialog(QDialog):
    def __init__(self, parent, default_x=0, default_width=50, default_color=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Stripe")
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(0, RIBBON_WIDTH)
        self.x_slider.setValue(default_x)
        self.x_label = QLabel(f"X: {default_x}")
        self.x_slider.valueChanged.connect(lambda v: self.x_label.setText(f"X: {v}"))

        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, RIBBON_WIDTH)
        self.width_slider.setValue(default_width)
        self.width_label = QLabel(f"Width: {default_width}")
        self.width_slider.valueChanged.connect(lambda v: self.width_label.setText(f"Width: {v}"))

        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        self.color = default_color or QColor("#000000")
        self.update_color_button()

        layout.addWidget(self.x_label)
        layout.addWidget(self.x_slider)
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_slider)
        layout.addWidget(self.color_button)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.color)
        if color.isValid():
            self.color = color
            self.update_color_button()

    def update_color_button(self):
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")

    def get_values(self):
        return self.x_slider.value(), self.width_slider.value(), self.color