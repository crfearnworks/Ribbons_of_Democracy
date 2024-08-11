import json

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

    def add_device(self, name, color, x, y):
        self.data['devices'].append({'name': name, 'color': color, 'x': x, 'y': y})

    def set_background(self, color):
        self.data['background'] = color

    def remove_stripe(self, index):
        del self.data['stripes'][index]

    def remove_device(self, index):
        del self.data['devices'][index]

    def edit_stripe(self, index, x, width, color, mirrored):
        self.data['stripes'][index] = {'x': x, 'width': width, 'color': color, 'mirrored': mirrored}

    def edit_device(self, index, name, color, x, y):
        self.data['devices'][index] = {'name': name, 'color': color, 'x': x, 'y': y}

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