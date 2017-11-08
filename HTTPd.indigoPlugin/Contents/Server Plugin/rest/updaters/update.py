from dimmer import Dimmer
from switch import Switch

targets = [Dimmer(), Switch()]
def update(device, actions, prefs):
    for target in targets:
        if target.can_handle(device, prefs):
            return target.update(device, actions)