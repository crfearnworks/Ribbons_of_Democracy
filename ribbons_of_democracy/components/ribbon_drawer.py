import os
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QPoint

RIBBON_WIDTH = 1024
RIBBON_HEIGHT = 282

class RibbonDrawer:
    @staticmethod
    def draw_ribbon(ribbon_data, painter=None, draw_outline=False, exclude_devices=False):
        width, height = RIBBON_WIDTH, RIBBON_HEIGHT
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
            painter.fillRect(stripe['x'], 0, stripe['width'], height, QColor(stripe['color']))
            if stripe.get('mirrored', False):
                mirrored_x = width - stripe['x'] - stripe['width']
                painter.fillRect(mirrored_x, 0, stripe['width'], height, QColor(stripe['color']))
        
        # Apply texture if enabled
        if ribbon_data.data['texture_enabled']:
            RibbonDrawer.apply_texture(painter, width, height)
        
        # Draw devices
        if not exclude_devices:
            devices = ribbon_data.data['devices']
            total_width = sum(device['width'] for device in devices)
            available_width = RIBBON_WIDTH * 0.8  # 80% of ribbon width
            if total_width > available_width:
                scale_factor = available_width / total_width
                for device in devices:
                    device['width'] = int(device['width'] * scale_factor)
                    device['height'] = int(device['height'] * scale_factor)

            max_height = RIBBON_HEIGHT // 3  # One-third of the ribbon height
            x_offset = (RIBBON_WIDTH - total_width) // 2
            for device in devices:
                device_pixmap = QPixmap(device['path'])
                scaled_height = min(device['height'], max_height)
                scaled_width = int(scaled_height * (device['width'] / device['height']))
                scaled_pixmap = device_pixmap.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                y_offset = (RIBBON_HEIGHT - scaled_height) // 2
                painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
                x_offset += scaled_width
        
        # Draw logo if set
        if ribbon_data.data['logo']:
            logo_pixmap = QPixmap(ribbon_data.data['logo'])
            logo_height = RIBBON_HEIGHT - 40  # 20 pixels from top and bottom
            logo_width = int(logo_height * (logo_pixmap.width() / logo_pixmap.height()))
            scaled_logo = logo_pixmap.scaled(logo_width, logo_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_x = (RIBBON_WIDTH - logo_width) // 2
            logo_y = 20  # 20 pixels from the top
            painter.drawPixmap(logo_x, logo_y, scaled_logo)

        # Draw frame if set
        if ribbon_data.data['frame']:
            frame_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frames', f"{ribbon_data.data['frame'].capitalize()}-Frame.png")
            frame_pixmap = QPixmap(frame_path)
            scaled_frame = frame_pixmap.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_frame)
        
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
        for i, _ in enumerate(range(0, height, 2)):
            texture_painter.setPen(QColor(0, 0, 0, 20))
            texture_painter.drawLine(0, i * 2, width, i * 2)
        
        texture_painter.end()
        
        # Apply texture with alpha blending
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, texture)

    @staticmethod
    def save_as_png(ribbon_data, filename):
        original_width, original_height = RIBBON_WIDTH, RIBBON_HEIGHT
        target_width, target_height = 1024, 282

        pixmap = RibbonDrawer.draw_ribbon(ribbon_data, draw_outline=False)
        
        # Downscale the image
        scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        scaled_pixmap.save(filename, "PNG")