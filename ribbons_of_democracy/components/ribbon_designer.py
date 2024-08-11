from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QColorDialog, QDialog, QInputDialog
from PyQt6.QtGui import QKeySequence, QShortcut, QColor, QPixmap, QPainter
from PyQt6.QtCore import Qt
from .ribbon_data import RibbonData
from .ribbon_drawer import RibbonDrawer
from .ui_components import get_stripe_input, get_device_input, select_item
from .device_selector import DeviceSelector
import copy

class RibbonDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ribbon Designer")
        self.ribbon_data = RibbonData()
        self.ui_scale_factor = 0.5  # Scale factor for UI display
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.ribbon_label = QLabel()
        self.ribbon_label.setFixedSize(int(1448 * self.ui_scale_factor), int(399 * self.ui_scale_factor))
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
            ("Undo", self.undo_last_action),
            ("Toggle Mirror", self.toggle_mirror_stripe),
            ("Toggle Texture", self.toggle_texture),
            ("Save as PNG", self.save_as_png)
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
        pixmap = RibbonDrawer.draw_ribbon(self.ribbon_data, draw_outline=True)
        scaled_pixmap = pixmap.scaled(int(1448 * self.ui_scale_factor), int(399 * self.ui_scale_factor), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        self.ribbon_label.setPixmap(scaled_pixmap)

    def clear_all(self):
        self.ribbon_data = RibbonData()
        self.draw_ribbon()

    def undo_last_action(self):
        if len(self.history) > 1:
            self.history.pop()  # Remove the current state
            self.ribbon_data.data = copy.deepcopy(self.history[-1])
            self.draw_ribbon()

    def add_stripe(self):
        result = get_stripe_input(self)
        if result:
            x, width, color = result
            # Convert UI coordinates to internal coordinates
            internal_x = int(x * 1448 / 300)
            internal_width = int(width * 1448 / 300)
            self.ribbon_data.add_stripe(internal_x, internal_width, color)
            self.draw_ribbon()

    def edit_stripe(self):
        index = select_item(self, "Edit Stripe", "Select stripe to edit:", 
                            [f"Stripe at ({s['x']}, width: {s['width']})" for s in self.ribbon_data.data['stripes']])
        if index is not None:
            stripe = self.ribbon_data.data['stripes'][index]
            # Convert internal coordinates to UI coordinates
            ui_x = int(stripe['x'] * 300 / 1448)
            ui_width = int(stripe['width'] * 300 / 1448)
            result = get_stripe_input(self, ui_x, ui_width)
            if result:
                x, width, color = result
                # Convert UI coordinates back to internal coordinates
                internal_x = int(x * 1448 / 300)
                internal_width = int(width * 1448 / 300)
                self.ribbon_data.edit_stripe(index, internal_x, internal_width, color, stripe['mirrored'])
                self.draw_ribbon()

    def add_device(self):
        device_selector = DeviceSelector(self, self.ribbon_data.load_available_devices())
        if device_selector.exec():
            selected_device = device_selector.selected_device
            x, ok1 = QInputDialog.getInt(self, "Device Position", "Enter X coordinate:", 0, 0, 300)
            y, ok2 = QInputDialog.getInt(self, "Device Position", "Enter Y coordinate:", 50, 0, 100)
            if ok1 and ok2:
                # Convert UI coordinates to internal coordinates
                internal_x = int(x * 1448 / 300)
                internal_y = int(y * 399 / 100)
                device_pixmap = QPixmap(selected_device['path'])
                aspect_ratio = device_pixmap.width() / device_pixmap.height()
                internal_height = int(50 * 399 / 100)  # Default to 50% of ribbon height
                internal_width = int(internal_height * aspect_ratio)
                self.ribbon_data.add_device(selected_device['name'], selected_device['path'], 
                                            internal_x, internal_y, internal_width, internal_height)
                self.draw_ribbon()

    def edit_device(self):
        index = select_item(self, "Edit Device", "Select device to edit:", 
                            [f"{d['name']} at ({d['x']}, {d['y']})" for d in self.ribbon_data.data['devices']])
        if index is not None:
            device = self.ribbon_data.data['devices'][index]
            # Convert internal coordinates to UI coordinates
            ui_x = int(device['x'] * 300 / 1448)
            ui_y = int(device['y'] * 100 / 399)
            name, color, x, y = get_device_input(self, device['name'], ui_x, ui_y)
            if name is not None:
                # Convert UI coordinates back to internal coordinates
                internal_x = int(x * 1448 / 300)
                internal_y = int(y * 399 / 100)
                self.ribbon_data.edit_device(index, name, color, internal_x, internal_y)
                self.draw_ribbon()

    def remove_stripe(self):
        index = select_item(self, "Remove Stripe", "Select stripe to remove:", [f"Stripe at x={s['x']}, width={s['width']}" for s in self.ribbon_data.data['stripes']])
        if index is not None:
            self.ribbon_data.remove_stripe(index)
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

    def save_as_png(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Ribbon as PNG", "", "PNG Files (*.png)")
        if filename:
            RibbonDrawer.save_as_png(self.ribbon_data, filename)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.ribbon_label.mapFrom(self, event.pos())
            if 0 <= pos.x() <= int(1448 * self.ui_scale_factor) and 0 <= pos.y() <= int(399 * self.ui_scale_factor):
                self.place_device(pos.x(), pos.y())

    def place_device(self, x, y):
        device_input = get_device_input(self, default_x=x, default_y=y)
        if device_input:
            name, color, x, y = device_input
            # Convert UI coordinates to internal coordinates
            internal_x = int(x * 1448 / 300)
            internal_y = int(y * 399 / 100)
            self.ribbon_data.add_device(name, color, internal_x, internal_y)
            self.draw_ribbon()

    def toggle_mirror_stripe(self):
        index = select_item(self, "Toggle Mirror Stripe", "Select stripe to mirror:", [f"Stripe at x={s['x']}, width={s['width']}" for s in self.ribbon_data.data['stripes']])
        if index is not None:
            stripe = self.ribbon_data.data['stripes'][index]
            stripe['mirrored'] = not stripe.get('mirrored', False)
            self.draw_ribbon()

    def toggle_texture(self):
        self.ribbon_data.data['texture_enabled'] = not self.ribbon_data.data['texture_enabled']
        self.draw_ribbon()

    def load_available_devices(self):
        self.available_devices = self.ribbon_data.load_available_devices()