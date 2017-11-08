from __future__ import division
from formatter import Formatter
import indigo
import colorsys

class Dimmer(Formatter):
    def can_format(self, device, prefs):
        return isinstance(device, indigo.DimmerDevice)

    def to_dictionary(self, device):
        base = super(Dimmer, self).to_dictionary(device)
        base['type'] = 'dimmer'
        base['on'] = device.onState
        base['brightness'] = device.brightness
        base['supportsWhiteTemperature'] = device.supportsWhite
        base['supportsHSV'] = device.supportsRGB
        base['supportsOnOff'] = True
        base['supportsDim'] = True

        if device.supportsWhite:
            base['whiteTemperature'] = device.whiteTemperature
        
        if device.supportsRGB:
            hsv = colorsys.rgb_to_hsv(device.redLevel / 255, device.greenLevel / 255, device.blueLevel / 255)
            base['saturation'] = hsv[1] * 100
            base['hue'] = hsv[0] * 360

        return base