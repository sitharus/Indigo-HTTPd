class Formatter(object):
    def can_format(self, device):
        return False

    def to_dictionary(self, device):
        return {'name': device.name, 'id': device.id, 'description': device.description}
