from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QFileDialog, QColorDialog, QDialog, QInputDialog, QMessageBox
from PyQt6.QtGui import QKeySequence, QShortcut, QColor, QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt, QSize
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
        self.setWindowTitle("Ribbons of Democracy")
        self.set_window_icon()
        self.ribbon_data = RibbonData()
        self.ui_scale_factor = 0.5  # Scale factor for UI display
        self.init_ui()

    def set_window_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', '07 Skull White.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("Warning: Window icon not found.")

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { 
                background-color: #3c3f41; 
                color: #ffffff; 
                border: 1px solid #555555;
                padding: 5px;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover { background-color: #4c5052; }
            QLabel { background-color: #1e1e1e; border: 1px solid #555555; }
            QLabel.group-label { 
                background-color: #4c5052; 
                color: #ffffff; 
                font-weight: bold; 
                padding: 5px;
                border-radius: 5px;
            }
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
            ("Misc", [("Background", self.change_background), ("Clear All", self.clear_all), ("Undo", self.undo_last_action),
                      ("Toggle Mirror", self.toggle_mirror_stripe), ("Toggle Texture", self.toggle_texture)]),
            ("Super Earth Logo", [("Add Logo", self.add_logo), ("Remove Logo", self.remove_logo)]),
            ("Help", [("About", self.show_about)]),
            ("Ribbon Info", [("Edit Info", self.edit_ribbon_info), ("View Info", self.view_ribbon_info)])
        ]

        for group_name, buttons in button_groups:
            group_layout = QVBoxLayout()
            group_label = QLabel(group_name)
            group_label.setProperty("class", "group-label")
            group_layout.addWidget(group_label)

            grid_layout = QGridLayout()
            grid_layout.setSpacing(5)
            for i, (text, func) in enumerate(buttons):
                button = QPushButton(QIcon(self.get_icon_path(text.lower().replace(' ', '_'))), text)
                button.clicked.connect(func)
                button.setIconSize(QSize(16, 16))  # Set a smaller icon size
                button.setFixedSize(120, 40)  # Set a fixed size for all buttons
                grid_layout.addWidget(button, i // 2, i % 2)

            group_layout.addLayout(grid_layout)
            button_layout.addLayout(group_layout)
            button_layout.addSpacing(5)  # Reduce spacing between groups

        main_layout.addLayout(button_layout)
        self.draw_ribbon()

    def get_icon_path(self, icon_name):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', f'{icon_name}.png')
        return icon_path if os.path.exists(icon_path) else ''

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
            result = get_stripe_input(self, stripe['x'], stripe['width'])
            if result:
                x, width, color = result
                self.ribbon_data.edit_stripe(index, x, width, color, stripe['mirrored'])
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
            x = (RIBBON_WIDTH - width) // 2  # Center horizontally
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
                x = (RIBBON_WIDTH - width) // 2  # Center horizontally
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
            self.ribbon_data.add_device(name, color, x, y)
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

    def add_logo(self):
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo', 'Super Earth Brand 03 White.png')
        if os.path.exists(logo_path):
            self.ribbon_data.set_logo(logo_path)
            self.draw_ribbon()
        else:
            QMessageBox.warning(self, "Logo Not Found", "The Super Earth logo file was not found in the logo directory.")

    def remove_logo(self):
        self.ribbon_data.remove_logo()
        self.draw_ribbon()

    def show_about(self):
        about_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ABOUT.md')
        try:
            with open(about_path, 'r', encoding='utf-8') as file:
                about_text = file.read()
            QMessageBox.about(self, "About Ribbons of Democracy", about_text)
        except FileNotFoundError:
            QMessageBox.warning(self, "About File Not Found", "The ABOUT.md file was not found.")

    def edit_ribbon_info(self):
        current_info = self.ribbon_data.get_ribbon_info()
        name, ok1 = QInputDialog.getText(self, "Ribbon Name", "Enter ribbon name:", text=current_info['name'])
        if ok1:
            award_details, ok2 = QInputDialog.getMultiLineText(self, "Award Details", "Enter award details:", current_info['award_details'])
            if ok2:
                device_details, ok3 = QInputDialog.getMultiLineText(self, "Device Details", "Enter device details:", current_info['device_details'])
                if ok3:
                    self.ribbon_data.set_ribbon_info(name, award_details, device_details)

    def view_ribbon_info(self):
        info = self.ribbon_data.get_ribbon_info()
        message = f"Ribbon Name: {info['name']}\n\n"
        message += f"Award Details:\n{info['award_details']}\n\n"
        message += f"Device Details:\n{info['device_details']}"
        QMessageBox.information(self, "Ribbon Information", message)