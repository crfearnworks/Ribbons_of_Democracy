from PyQt6.QtWidgets import QInputDialog, QColorDialog, QMessageBox
from .ribbon_drawer import RIBBON_WIDTH, RIBBON_HEIGHT

def get_stripe_input(parent, default_x=0, default_width=50):
    color = QColorDialog.getColor()
    if color.isValid():
        x, ok1 = QInputDialog.getInt(parent, "Stripe Position", "Enter X coordinate:", default_x, 0, RIBBON_WIDTH)
        width, ok2 = QInputDialog.getInt(parent, "Stripe Width", "Enter width:", default_width, 1, RIBBON_WIDTH)
        if ok1 and ok2:
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