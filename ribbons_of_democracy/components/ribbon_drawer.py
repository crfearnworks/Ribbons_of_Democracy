from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

class RibbonDrawer:
    @staticmethod
    def draw_ribbon(ribbon_data):
        pixmap = QPixmap(300, 100)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        # Draw background
        painter.fillRect(0, 0, 300, 100, QColor(ribbon_data.data['background']))
        
        # Draw stripes
        for stripe in ribbon_data.data['stripes']:
            painter.fillRect(stripe['x'], 0, stripe['width'], 100, QColor(stripe['color']))
            if stripe['mirrored']:
                mirrored_x = 300 - stripe['x'] - stripe['width']
                painter.fillRect(mirrored_x, 0, stripe['width'], 100, QColor(stripe['color']))
        
        # Draw devices
        for device in ribbon_data.data['devices']:
            painter.setPen(QColor(device['color']))
            painter.drawText(device['x'], device['y'], device['name'])
        
        # Draw preview for device placement
        painter.setPen(Qt.PenStyle.DashLine)
        painter.drawRect(0, 0, 300, 100)
        
        painter.end()
        return pixmap