from formatter import Formatter
import indigo

class Dimmer(Formatter):
    def can_format(self, device):
        return isinstance(device, indigo.DimmerDevice)

    def to_dictionary(self, device):
        base = super(Dimmer, self).to_dictionary(device)
        base['kind'] = 'dimmer'
        base['on'] = device.onState
        base['brightness'] = device.brightness
        base['supportsWhite'] = device.supportsWhite
        base['supportsRGB'] = device.supportsRGB

        if device.supportsWhite:
            base['whiteTemperature'] = device.whiteTemperature
        
        if device.supportsRGB:
            base['rgb'] = {'red': device.redLevel, 'green': device.greenLevel, 'blue': device.blueLevel}

        return base