import json
import os
from pathlib import Path

class RibbonData:
    def __init__(self):
        self.data = {
            'background': '#000000',
            'stripes': [],
            'devices': [],
            'texture_enabled': False,
            'frame': None,  # Can be 'gold', 'silver', or None
            'logo': None,  # Will store the path to the logo image
            'info': {
                'name': '',
                'award_details': '',
                'device_details': ''
            }
        }

    def add_stripe(self, x, width, color, mirrored=False):
        self.data['stripes'].append({'x': x, 'width': width, 'color': color, 'mirrored': mirrored})

    def add_device(self, name, path, x, y, width, height):
        self.data['devices'].append({'name': name, 'path': path, 'x': x, 'y': y, 'width': width, 'height': height})

    def set_background(self, color):
        self.data['background'] = color

    def remove_stripe(self, index):
        del self.data['stripes'][index]

    def remove_device(self, index):
        del self.data['devices'][index]

    def edit_stripe(self, index, x, width, color, mirrored):
        self.data['stripes'][index] = {'x': x, 'width': width, 'color': color, 'mirrored': mirrored}

    def edit_device(self, index, name, color_or_path, x, y, width=None, height=None):
        device = self.data['devices'][index]
        device['name'] = name
        device['x'] = x
        device['y'] = y
        if width is not None and height is not None:
            device['path'] = color_or_path
            device['width'] = width
            device['height'] = height
        else:
            device['color'] = color_or_path

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        if data.get('logo'):
            logo_path = os.path.join(os.path.dirname(filename), data['logo'])
            if os.path.exists(logo_path):
                data['logo'] = logo_path
            else:
                print(f"Warning: Logo file not found at {logo_path}")
                data['logo'] = None
        self.data = data

    def save_to_file(self, filename):
        data_to_save = self.data.copy()
        if data_to_save.get('logo'):
            data_to_save['logo'] = os.path.relpath(data_to_save['logo'], os.path.dirname(filename))
        with open(filename, 'w') as file:
            json.dump(data_to_save, file)

    def set_frame(self, frame_type):
        if frame_type in ['gold', 'silver', None]:
            self.data['frame'] = frame_type
            if frame_type:
                frame_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frames', f"{frame_type.capitalize()}-Frame.png")
                if not os.path.exists(frame_path):
                    print(f"Warning: Frame file not found at {frame_path}")
                    self.data['frame'] = None

    def remove_frame(self):
        self.data['frame'] = None

    def clear(self):
        self.data = {
            'background': '#000000',
            'stripes': [],
            'devices': [],
            'texture_enabled': False,
            'frame': None,  # Can be 'gold', 'silver', or None
            'logo': None,  # Will store the path to the logo image
            'info': {
                'name': '',
                'award_details': '',
                'device_details': ''
            }
        }

    def load_available_devices(self):
        devices_dir = Path(__file__).parent.parent / 'standard_devices'
        available_devices = []
        for file in devices_dir.glob('*.png'):
            available_devices.append({
                'name': file.stem,
                'path': str(file)
            })
        return available_devices

    def set_logo(self, logo_path):
        self.data['logo'] = logo_path

    def remove_logo(self):
        self.data['logo'] = None

    def set_ribbon_info(self, name, award_details, device_details):
        self.data['info'] = {
            'name': name,
            'award_details': award_details,
            'device_details': device_details
        }

    def get_ribbon_info(self):
        return self.data['info']