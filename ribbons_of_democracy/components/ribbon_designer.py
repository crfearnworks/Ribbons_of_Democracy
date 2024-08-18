from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QColorDialog, QDialog, QInputDialog
from PyQt6.QtGui import QKeySequence, QShortcut, QColor, QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt
from .ribbon_data import RibbonData
from .ribbon_drawer import RibbonDrawer
from .ui_components import get_stripe_input, get_device_input, select_item
from .device_selector import DeviceSelector
import copy
import os

RIBBON_WIDTH = 1024
RIBBON_HEIGHT = 282

class RibbonDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ribbon Designer")
        self.ribbon_data = RibbonData()
        self.ui_scale_factor = 0.5  # Scale factor for UI display
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { 
                background-color: #3c3f41; 
                color: #ffffff; 
                border: 1px solid #555555;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #4c5052; }
            QLabel { background-color: #1e1e1e; border: 1px solid #555555; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.ribbon_label = QLabel()
        self.ribbon_label.setFixedSize(RIBBON_WIDTH, RIBBON_HEIGHT)
        self.ribbon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.ribbon_label)

        button_layout = QHBoxLayout()
        button_groups = [
            ("File", [("Import", self.import_ribbon), ("Export", self.export_ribbon), ("Save as PNG", self.save_as_png)]),
            ("Edit", [("Add Stripe", self.add_stripe), ("Edit Stripe", self.edit_stripe), ("Remove Stripe", self.remove_stripe)]),
            ("Devices", [("Add Device", self.add_device), ("Edit Device", self.edit_device), ("Remove Device", self.remove_device)]),
            ("Frame", [("Add Gold Frame", self.add_gold_frame), ("Add Silver Frame", self.add_silver_frame), ("Remove Frame", self.remove_frame)]),
            ("Misc", [("Change Background", self.change_background), ("Clear All", self.clear_all), ("Undo", self.undo_last_action),
                      ("Toggle Mirror", self.toggle_mirror_stripe), ("Toggle Texture", self.toggle_texture)])
        ]

        for group_name, buttons in button_groups:
            group_layout = QVBoxLayout()
            group_layout.addWidget(QLabel(group_name))
            for text, func in buttons:
                button = QPushButton(QIcon(self.get_icon_path(text.lower().replace(' ', '_'))), text)
                button.clicked.connect(func)
                group_layout.addWidget(button)
            button_layout.addLayout(group_layout)

        main_layout.addLayout(button_layout)
        self.draw_ribbon()

    def get_icon_path(self, icon_name):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', f'{icon_name}.png')

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_last_action)
        QShortcut(QKeySequence("Ctrl+N"), self, self.clear_all)
        QShortcut(QKeySequence("Ctrl+S"), self, self.export_ribbon)
        QShortcut(QKeySequence("Ctrl+O"), self, self.import_ribbon)

    def draw_ribbon(self):
        pixmap = RibbonDrawer.draw_ribbon(self.ribbon_data, draw_outline=True)
        self.ribbon_label.setPixmap(pixmap)

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
            self.ribbon_data.add_stripe(x, width, color)
            self.draw_ribbon()

    def edit_stripe(self):
        index = select_item(self, "Edit Stripe", "Select stripe to edit:", 
                            [f"Stripe at ({s['x']}, width: {s['width']})" for s in self.ribbon_data.data['stripes']])
        if index is not None:
            stripe = self.ribbon_data.data['stripes'][index]
            # Convert internal coordinates to UI coordinates
            ui_x = int(stripe['x'] * RIBBON_WIDTH / SCALE_X)
            ui_width = int(stripe['width'] * RIBBON_WIDTH / SCALE_X)
            result = get_stripe_input(self, ui_x, ui_width)
            if result:
                x, width, color = result
                # Convert UI coordinates back to internal coordinates
                internal_x = int(x / SCALE_X)
                internal_width = int(width / SCALE_X)
                self.ribbon_data.edit_stripe(index, internal_x, internal_width, color, stripe['mirrored'])
                self.draw_ribbon()

    def add_device(self):
        device_selector = DeviceSelector(self, self.ribbon_data.load_available_devices())
        if device_selector.exec():
            selected_device = device_selector.selected_device
            device_pixmap = QPixmap(selected_device['path'])
            aspect_ratio = device_pixmap.width() / device_pixmap.height()
            max_height = RIBBON_HEIGHT // 3  # One-third of the ribbon height
            height = min(int(RIBBON_HEIGHT * 0.3), max_height)
            width = int(height * aspect_ratio)
            x = 0  # Will be adjusted when drawing
            y = (RIBBON_HEIGHT - height) // 2  # Center vertically
            self.ribbon_data.add_device(selected_device['name'], selected_device['path'], 
                                        x, y, width, height)
            self.draw_ribbon()

    def edit_device(self):
        index = select_item(self, "Edit Device", "Select device to edit:", 
                            [f"{d['name']}" for d in self.ribbon_data.data['devices']])
        if index is not None:
            device = self.ribbon_data.data['devices'][index]
            device_selector = DeviceSelector(self, self.ribbon_data.load_available_devices())
            if device_selector.exec():
                selected_device = device_selector.selected_device
                device_pixmap = QPixmap(selected_device['path'])
                aspect_ratio = device_pixmap.width() / device_pixmap.height()
                max_height = RIBBON_HEIGHT // 3  # One-third of the ribbon height
                height = min(int(RIBBON_HEIGHT * 0.3), max_height)
                width = int(height * aspect_ratio)
                x = 0  # Will be adjusted when drawing
                y = (RIBBON_HEIGHT - height) // 2  # Center vertically
                self.ribbon_data.edit_device(index, selected_device['name'], selected_device['path'], 
                                             x, y, width, height)
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
            if 0 <= pos.x() <= RIBBON_WIDTH and 0 <= pos.y() <= RIBBON_HEIGHT:
                self.place_device(pos.x(), pos.y())

    def place_device(self, x, y):
        device_input = get_device_input(self, default_x=x, default_y=y)
        if device_input:
            name, color, x, y = device_input
            # Convert UI coordinates to internal coordinates
            internal_x = int(x / SCALE_X)
            internal_y = int(y / SCALE_Y)
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
        
    def add_gold_frame(self):
        self.ribbon_data.set_frame('gold')
        self.draw_ribbon()

    def add_silver_frame(self):
        self.ribbon_data.set_frame('silver')
        self.draw_ribbon()

    def remove_frame(self):
        self.ribbon_data.remove_frame()
        self.draw_ribbon()