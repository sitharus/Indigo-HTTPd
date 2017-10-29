from dimmer import Dimmer

targets = [Dimmer()]
def update(device, actions):
    for target in targets:
        if target.can_handle(device):
            return target.update(device, actions)