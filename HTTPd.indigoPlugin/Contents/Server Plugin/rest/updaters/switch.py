import indigo

class Switch(object):
    def can_handle(self, device, prefs):
        ids = prefs.get("lightSwitchIds")
        if ids is not None:
           lights = [int(x) for x in ids.split(',')]
           if device.id in lights:
               return True
        return False

    def update(self, device, actions):
        for key, values in actions.items():
            value = values[0]
            if key == "on":
                if bool(value) and value != "0":
                    indigo.device.turnOn(device)
                else:
                    indigo.device.turnOff(device)
