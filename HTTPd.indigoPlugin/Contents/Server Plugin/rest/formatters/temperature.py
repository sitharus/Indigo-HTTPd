from formatter import Formatter
import indigo

class Temperature(Formatter):
    def can_format(self, device, prefs):
        return (isinstance(device, indigo.SensorDevice) and 
            device.displayStateImageSel == indigo.kStateImageSel.TemperatureSensor)

    def to_dictionary(self, device):
        base = super(Temperature, self).to_dictionary(device)
        base['type'] = 'temperatureSensor'
        base['temperature'] = device.sensorValue
        return base
