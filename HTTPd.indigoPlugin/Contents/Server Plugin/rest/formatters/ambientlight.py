from formatter import Formatter
import indigo

class Light(Formatter):
    def can_format(self, device, prefs):
        return (isinstance(device, indigo.SensorDevice) and 
            device.displayStateImageSel == indigo.kStateImageSel.LightSensor)

    def to_dictionary(self, device):
        base = super(Light, self).to_dictionary(device)
        base['type'] = 'lightSensor'
        base['lightLevel'] = device.sensorValue
        return base
