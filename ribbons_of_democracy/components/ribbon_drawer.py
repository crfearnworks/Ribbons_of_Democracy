from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QPoint

class RibbonDrawer:
    @staticmethod
    def draw_ribbon(ribbon_data, painter=None):
        if painter is None:
            pixmap = QPixmap(300, 100)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            should_end_painter = True
        else:
            should_end_painter = False

        # Draw background
        painter.fillRect(0, 0, 300, 100, QColor(ribbon_data.data['background']))
        
        # Draw stripes
        for stripe in ribbon_data.data['stripes']:
            painter.fillRect(stripe['x'], 0, stripe['width'], 100, QColor(stripe['color']))
            if stripe['mirrored']:
                mirrored_x = 300 - stripe['x'] - stripe['width']
                painter.fillRect(mirrored_x, 0, stripe['width'], 100, QColor(stripe['color']))
        
        # Apply texture if enabled
        if ribbon_data.data['texture_enabled']:
            RibbonDrawer.apply_texture(painter, 300, 100)
        
        # Draw devices
        for device in ribbon_data.data['devices']:
            painter.setPen(QColor(device['color']))
            painter.drawText(device['x'], device['y'], device['name'])
        
        # Draw preview for device placement
        painter.setPen(Qt.PenStyle.DashLine)
        painter.drawRect(0, 0, 300, 100)
        
        if should_end_painter:
            painter.end()
            return pixmap

    @staticmethod
    def apply_texture(painter, width, height):
        texture = QPixmap(width, height)
        texture.fill(Qt.GlobalColor.transparent)
        texture_painter = QPainter(texture)
        
        # Create horizontal lines
        for y in range(0, height, 2):
            texture_painter.setPen(QColor(0, 0, 0, 20))
            texture_painter.drawLine(0, y, width, y)
        
        texture_painter.end()
        
        # Apply texture with alpha blending
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, texture)

    @staticmethod
    def save_as_png(ribbon_data, filename, scale=4):
        width, height = 300 * scale, 100 * scale
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.scale(scale, scale)
        
        RibbonDrawer.draw_ribbon(ribbon_data, painter)
        painter.end()
        
        pixmap.save(filename, "PNG")