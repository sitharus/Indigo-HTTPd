import unknown
import dimmer
import switch

formatter_list = [dimmer.Dimmer(), switch.Switch(), unknown.Unknown()]
def format_device(device, prefs):
    for item in formatter_list:
        if item.can_format(device, prefs):
            return item.to_dictionary(device)