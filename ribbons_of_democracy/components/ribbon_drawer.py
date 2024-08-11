from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QPoint

class RibbonDrawer:
    @staticmethod
    def draw_ribbon(ribbon_data, painter=None, draw_outline=False, exclude_devices=False):
        width, height = 1448, 399
        if painter is None:
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            should_end_painter = True
        else:
            should_end_painter = False

        # Draw background
        painter.fillRect(0, 0, width, height, QColor(ribbon_data.data['background']))
        
        # Draw stripes
        for stripe in ribbon_data.data['stripes']:
            scaled_x = int(stripe['x'] * width / 300)
            scaled_width = int(stripe['width'] * width / 300)
            painter.fillRect(scaled_x, 0, scaled_width, height, QColor(stripe['color']))
            if stripe['mirrored']:
                mirrored_x = width - scaled_x - scaled_width
                painter.fillRect(mirrored_x, 0, scaled_width, height, QColor(stripe['color']))
        
        # Apply texture if enabled
        if ribbon_data.data['texture_enabled']:
            RibbonDrawer.apply_texture(painter, width, height)
        
        # Draw devices
        if not exclude_devices:
            for device in ribbon_data.data['devices']:
                scaled_x = int(device['x'] * width / 300)
                scaled_y = int(device['y'] * height / 100)
                if device['path'].startswith('#'):
                    painter.setPen(QColor(device['path']))
                    font = painter.font()
                    font.setPointSize(int(12 * height / 100))
                    painter.setFont(font)
                    painter.drawText(scaled_x, scaled_y, device['name'])
                else:
                    device_pixmap = QPixmap(device['path'])
                    scaled_width = int(device['width'] * width / 300)
                    scaled_height = int(device['height'] * height / 100)
                    scaled_pixmap = device_pixmap.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    painter.drawPixmap(scaled_x, scaled_y, scaled_pixmap)
        
        # Draw preview outline only if requested
        if draw_outline:
            painter.setPen(Qt.PenStyle.DashLine)
            painter.drawRect(0, 0, width, height)
        
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
    def save_as_png(ribbon_data, filename):
        original_width, original_height = 1448, 399
        target_width, target_height = 1024, 282

        pixmap = QPixmap(original_width, original_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        RibbonDrawer.draw_ribbon(ribbon_data, painter, draw_outline=False)
        painter.end()

        # Downscale the image
        scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        scaled_pixmap.save(filename, "PNG")