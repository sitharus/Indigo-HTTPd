from __future__ import division
import indigo
import colorsys

class Dimmer(object):
    def can_handle(self, device):
        return isinstance(device, indigo.DimmerDevice)

    def update(self, device, actions):
        for key, values in actions.items():
            value = values[0]
            if key == "on":
                if bool(value) and value != "0":
                    indigo.device.turnOn(device)
                else:
                    indigo.device.turnOff(device)
            elif key == "brightness":
                indigo.dimmer.setBrightness(device, int(value))
            elif key == "saturation":
                hsv = colorsys.rgb_to_hsv(device.redLevel / 255, device.greenLevel / 255, device.blueLevel / 255)
                new = (hsv[0], float(value) / 100, hsv[2])
                rgb = colorsys.hsv_to_rgb(new[0], new[1], new[2])
                indigo.dimmer.setColorLevels(device, rgb[0] * 255, rgb[1] * 255, rgb[2] * 255, 0, 0, 0)
            elif key == "hue":
                hsv = colorsys.rgb_to_hsv(device.redLevel / 255, device.greenLevel / 255, device.blueLevel / 255)
                new = ((float(value) / 360), hsv[1], hsv[2])
                rgb = colorsys.hsv_to_rgb(new[0], new[1], new[2])
                indigo.dimmer.setColorLevels(device, rgb[0] * 255, rgb[1] * 255, rgb[2] * 255, 0, 0, 0)
            elif key == "whiteTemperature":
                indigo.dimmer.setColorLevels(device, None, None, None, None, None, int(value))

