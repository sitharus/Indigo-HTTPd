from formatter import Formatter
import indigo

class Motion(Formatter):
    def can_format(self, device, prefs):
        return (isinstance(device, indigo.SensorDevice) and 
            (device.displayStateImageSel == indigo.kStateImageSel.MotionSensor or
             device.displayStateImageSel == indigo.kStateImageSel.MotionSensorTripped
            ))

    def to_dictionary(self, device):
        base = super(Motion, self).to_dictionary(device)
        base['type'] = 'motionSensor'
        base['motionDetected'] = device.onState
        return base
