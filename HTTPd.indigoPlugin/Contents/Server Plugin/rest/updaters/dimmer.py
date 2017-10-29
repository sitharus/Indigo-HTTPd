import indigo

class Dimmer(object):
    def can_handle(self, device):
        return isinstance(device, indigo.DimmerDevice)

    def update(self, device, actions):
        for key, value in actions.items():
            if key == "on":
                if bool(value):
                    indigo.device.turnOn(device)
                else:
                    indigo.device.turnOff(device)
            elif key == "brightness":
                indigo.dimmer.brighten(device, int(value))
            elif key == "rgb":
                indigo.dimmer.setColorLevels(device, value['red'], value['green'], value['blue'], 0, 0, 0)
            elif key == "whiteTemperature":
                indigo.dimmer.setColorLevels(device, None, None, None, None, None, value)

