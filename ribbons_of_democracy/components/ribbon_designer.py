from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QColorDialog
from PyQt6.QtGui import QKeySequence, QShortcut, QColor
from PyQt6.QtCore import Qt
from .ribbon_data import RibbonData
from .ribbon_drawer import RibbonDrawer
from .ui_components import get_stripe_input, get_device_input, select_item
import copy

class RibbonDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ribbons of Democracy")
        self.setGeometry(100, 100, 800, 600)

        self.ribbon_data = RibbonData()
        self.history = [copy.deepcopy(self.ribbon_data.data)]
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.ribbon_label = QLabel()
        self.ribbon_label.setFixedSize(300, 100)
        self.ribbon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ribbon_label)

        button_layout = QHBoxLayout()
        buttons = [
            ("Import", self.import_ribbon),
            ("Export", self.export_ribbon),
            ("Add Stripe", self.add_stripe),
            ("Edit Stripe", self.edit_stripe),
            ("Remove Stripe", self.remove_stripe),
            ("Add Device", self.add_device),
            ("Edit Device", self.edit_device),
            ("Remove Device", self.remove_device),
            ("Change Background", self.change_background),
            ("Clear All", self.clear_all),
            ("Undo", self.undo_last_action)
        ]

        for text, func in buttons:
            button = QPushButton(text)
            button.clicked.connect(func)
            button_layout.addWidget(button)

        layout.addLayout(button_layout)
        self.draw_ribbon()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_last_action)
        QShortcut(QKeySequence("Ctrl+N"), self, self.clear_all)
        QShortcut(QKeySequence("Ctrl+S"), self, self.export_ribbon)
        QShortcut(QKeySequence("Ctrl+O"), self, self.import_ribbon)

    def draw_ribbon(self):
        pixmap = RibbonDrawer.draw_ribbon(self.ribbon_data)
        self.ribbon_label.setPixmap(pixmap)
        self.history.append(copy.deepcopy(self.ribbon_data.data))

    def clear_all(self):
        self.ribbon_data = RibbonData()
        self.draw_ribbon()

    def undo_last_action(self):
        if len(self.history) > 1:
            self.history.pop()  # Remove the current state
            self.ribbon_data.data = copy.deepcopy(self.history[-1])
            self.draw_ribbon()

    def add_stripe(self):
        stripe_input = get_stripe_input(self)
        if stripe_input:
            x, width, color = stripe_input
            self.ribbon_data.add_stripe(x, width, color)
            self.draw_ribbon()

    def edit_stripe(self):
        index = select_item(self, "Edit Stripe", "Select stripe to edit:", [f"Stripe at x={s['x']}, width={s['width']}" for s in self.ribbon_data.data['stripes']])
        if index is not None:
            stripe = self.ribbon_data.data['stripes'][index]
            x, width, color = get_stripe_input(self, stripe['x'], stripe['width'])
            if x is not None:
                self.ribbon_data.edit_stripe(index, x, width, color)
                self.draw_ribbon()

    def remove_stripe(self):
        index = select_item(self, "Remove Stripe", "Select stripe to remove:", [f"Stripe at x={s['x']}, width={s['width']}" for s in self.ribbon_data.data['stripes']])
        if index is not None:
            self.ribbon_data.remove_stripe(index)
            self.draw_ribbon()

    def add_device(self):
        device_input = get_device_input(self)
        if device_input:
            name, color, x, y = device_input
            self.ribbon_data.add_device(name, color, x, y)
            self.draw_ribbon()

    def edit_device(self):
        index = select_item(self, "Edit Device", "Select device to edit:", [f"{d['name']} at ({d['x']}, {d['y']})" for d in self.ribbon_data.data['devices']])
        if index is not None:
            device = self.ribbon_data.data['devices'][index]
            name, color, x, y = get_device_input(self, device['name'], device['x'], device['y'])
            if name is not None:
                self.ribbon_data.edit_device(index, name, color, x, y)
                self.draw_ribbon()

    def remove_device(self):
        index = select_item(self, "Remove Device", "Select device to remove:", [f"{d['name']} at ({d['x']}, {d['y']})" for d in self.ribbon_data.data['devices']])
        if index is not None:
            self.ribbon_data.remove_device(index)
            self.draw_ribbon()

    def change_background(self):
        color = QColorDialog.getColor(QColor(self.ribbon_data.data['background']))
        if color.isValid():
            self.ribbon_data.set_background(color.name())
            self.draw_ribbon()

    def import_ribbon(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Import Ribbon", "", "JSON Files (*.json)")
        if filename:
            self.ribbon_data.load_from_file(filename)
            self.draw_ribbon()

    def export_ribbon(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Ribbon", "", "JSON Files (*.json)")
        if filename:
            self.ribbon_data.save_to_file(filename)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.ribbon_label.mapFrom(self, event.pos())
            if 0 <= pos.x() <= 300 and 0 <= pos.y() <= 100:
                self.place_device(pos.x(), pos.y())

    def place_device(self, x, y):
        device_input = get_device_input(self, default_x=x, default_y=y)
        if device_input:
            name, color, x, y = device_input
            self.ribbon_data.add_device(name, color, x, y)
            self.draw_ribbon()