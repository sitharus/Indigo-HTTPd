from formatter import Formatter
import indigo

class Switch(Formatter):
    def can_format(self, device, prefs):
        ids = prefs.get("lightSwitchIds")
        if ids is not None:
           lights = [int(x) for x in ids.split(',')]
           if device.id in lights:
               return True
        return False

    def to_dictionary(self, device):
        base = super(Switch, self).to_dictionary(device)
        base['type'] = 'switch'
        base['on'] = device.onState
        base['supportsOnOff'] = True
        return base
