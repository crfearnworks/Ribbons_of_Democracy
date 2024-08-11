import json
import os
from pathlib import Path

class RibbonData:
    def __init__(self):
        self.data = {
            'background': '#000000',
            'stripes': [],
            'devices': [],
            'texture_enabled': False
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
            self.data = json.load(file)

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.data, file)

    def clear(self):
        self.data = {
            'background': '#000000',
            'stripes': [],
            'devices': [],
            'texture_enabled': False
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