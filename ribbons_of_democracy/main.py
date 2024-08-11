import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QColorDialog, QInputDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
import json

class RibbonDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ribbons of Democracy")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Ribbon display area
        self.ribbon_label = QLabel()
        self.ribbon_label.setFixedSize(300, 100)
        self.ribbon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ribbon_label)

        # Buttons
        button_layout = QHBoxLayout()
        import_button = QPushButton("Import")
        export_button = QPushButton("Export")
        add_stripe_button = QPushButton("Add Stripe")
        edit_stripe_button = QPushButton("Edit Stripe")
        remove_stripe_button = QPushButton("Remove Stripe")
        add_device_button = QPushButton("Add Device")
        edit_device_button = QPushButton("Edit Device")
        remove_device_button = QPushButton("Remove Device")
        change_background_button = QPushButton("Change Background")

        button_layout.addWidget(import_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(add_stripe_button)
        button_layout.addWidget(edit_stripe_button)
        button_layout.addWidget(remove_stripe_button)
        button_layout.addWidget(add_device_button)
        button_layout.addWidget(edit_device_button)
        button_layout.addWidget(remove_device_button)
        button_layout.addWidget(change_background_button)
        layout.addLayout(button_layout)

        # Connect buttons to functions
        import_button.clicked.connect(self.import_ribbon)
        export_button.clicked.connect(self.export_ribbon)
        add_stripe_button.clicked.connect(self.add_stripe)
        edit_stripe_button.clicked.connect(self.edit_stripe)
        remove_stripe_button.clicked.connect(self.remove_stripe)
        add_device_button.clicked.connect(self.add_device)
        edit_device_button.clicked.connect(self.edit_device)
        remove_device_button.clicked.connect(self.remove_device)
        change_background_button.clicked.connect(self.change_background)

        self.ribbon_data = {
            'background': '#000000',
            'stripes': [],
            'devices': []
        }
        self.draw_ribbon()

    def draw_ribbon(self):
        pixmap = QPixmap(300, 100)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        # Draw background
        painter.fillRect(0, 0, 300, 100, QColor(self.ribbon_data['background']))
        
        # Draw stripes
        for stripe in self.ribbon_data['stripes']:
            painter.fillRect(stripe['x'], 0, stripe['width'], 100, QColor(stripe['color']))
        
        # Draw devices
        for device in self.ribbon_data['devices']:
            painter.setPen(QColor(device['color']))
            painter.drawText(device['x'], device['y'], device['name'])
        
        # Draw preview for device placement
        painter.setPen(Qt.PenStyle.DashLine)
        painter.drawRect(0, 0, 300, 100)
        
        painter.end()
        self.ribbon_label.setPixmap(pixmap)

    def add_stripe(self):
        color = QColorDialog.getColor()
        if color.isValid():
            x, ok1 = QInputDialog.getInt(self, "Stripe Position", "Enter X coordinate:", 0, 0, 300)
            width, ok2 = QInputDialog.getInt(self, "Stripe Width", "Enter width:", 50, 1, 300)
            if ok1 and ok2:
                self.ribbon_data['stripes'].append({
                    'x': x,
                    'width': width,
                    'color': color.name()
                })
                self.draw_ribbon()

    def add_device(self):
        device, ok = QInputDialog.getText(self, "Add Device", "Enter device name:")
        if ok and device:
            color = QColorDialog.getColor()
            if color.isValid():
                x, ok1 = QInputDialog.getInt(self, "Device Position", "Enter X coordinate:", 0, 0, 300)
                y, ok2 = QInputDialog.getInt(self, "Device Position", "Enter Y coordinate:", 50, 0, 100)
                if ok1 and ok2:
                    self.ribbon_data['devices'].append({
                        'name': device,
                        'color': color.name(),
                        'x': x,
                        'y': y
                    })
                    self.draw_ribbon()

    def change_background(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.ribbon_data['background'] = color.name()
            self.draw_ribbon()

    def import_ribbon(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Ribbon", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as file:
                self.ribbon_data = json.load(file)
                self.draw_ribbon()

    def export_ribbon(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Ribbon", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(self.ribbon_data, file)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.ribbon_label.mapFrom(self, event.pos())
            if 0 <= pos.x() <= 300 and 0 <= pos.y() <= 100:
                self.place_device(pos.x(), pos.y())

    def place_device(self, x, y):
        device, ok = QInputDialog.getText(self, "Add Device", "Enter device name:")
        if ok and device:
            color = QColorDialog.getColor()
            if color.isValid():
                self.ribbon_data['devices'].append({
                    'name': device,
                    'color': color.name(),
                    'x': x,
                    'y': y
                })
                self.draw_ribbon()

    def remove_stripe(self):
        if not self.ribbon_data['stripes']:
            QMessageBox.information(self, "Remove Stripe", "No stripes to remove.")
            return
        items = [f"Stripe at x={s['x']}, width={s['width']}" for s in self.ribbon_data['stripes']]
        item, ok = QInputDialog.getItem(self, "Remove Stripe", "Select stripe to remove:", items, 0, False)
        if ok and item:
            index = items.index(item)
            del self.ribbon_data['stripes'][index]
            self.draw_ribbon()

    def remove_device(self):
        if not self.ribbon_data['devices']:
            QMessageBox.information(self, "Remove Device", "No devices to remove.")
            return
        items = [f"{d['name']} at ({d['x']}, {d['y']})" for d in self.ribbon_data['devices']]
        item, ok = QInputDialog.getItem(self, "Remove Device", "Select device to remove:", items, 0, False)
        if ok and item:
            index = items.index(item)
            del self.ribbon_data['devices'][index]
            self.draw_ribbon()

    def edit_stripe(self):
        if not self.ribbon_data['stripes']:
            QMessageBox.information(self, "Edit Stripe", "No stripes to edit.")
            return
        items = [f"Stripe at x={s['x']}, width={s['width']}" for s in self.ribbon_data['stripes']]
        item, ok = QInputDialog.getItem(self, "Edit Stripe", "Select stripe to edit:", items, 0, False)
        if ok and item:
            index = items.index(item)
            stripe = self.ribbon_data['stripes'][index]
            color = QColorDialog.getColor(QColor(stripe['color']))
            if color.isValid():
                x, ok1 = QInputDialog.getInt(self, "Stripe Position", "Enter X coordinate:", stripe['x'], 0, 300)
                width, ok2 = QInputDialog.getInt(self, "Stripe Width", "Enter width:", stripe['width'], 1, 300)
                if ok1 and ok2:
                    self.ribbon_data['stripes'][index] = {
                        'x': x,
                        'width': width,
                        'color': color.name()
                    }
                    self.draw_ribbon()

    def edit_device(self):
        if not self.ribbon_data['devices']:
            QMessageBox.information(self, "Edit Device", "No devices to edit.")
            return
        items = [f"{d['name']} at ({d['x']}, {d['y']})" for d in self.ribbon_data['devices']]
        item, ok = QInputDialog.getItem(self, "Edit Device", "Select device to edit:", items, 0, False)
        if ok and item:
            index = items.index(item)
            device = self.ribbon_data['devices'][index]
            name, ok1 = QInputDialog.getText(self, "Edit Device", "Enter new device name:", text=device['name'])
            if ok1 and name:
                color = QColorDialog.getColor(QColor(device['color']))
                if color.isValid():
                    x, ok2 = QInputDialog.getInt(self, "Device Position", "Enter X coordinate:", device['x'], 0, 300)
                    y, ok3 = QInputDialog.getInt(self, "Device Position", "Enter Y coordinate:", device['y'], 0, 100)
                    if ok2 and ok3:
                        self.ribbon_data['devices'][index] = {
                            'name': name,
                            'color': color.name(),
                            'x': x,
                            'y': y
                        }
                        self.draw_ribbon()

def main():
    app = QApplication(sys.argv)
    window = RibbonDesigner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()