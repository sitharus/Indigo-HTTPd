import unknown
import dimmer
import switch
import temperature
import ambientlight
import motion

formatter_list = [dimmer.Dimmer(), switch.Switch(), 
    temperature.Temperature(), ambientlight.Light(),
    motion.Motion(),
    unknown.Unknown()]
def format_device(device, prefs):
    for item in formatter_list:
        if item.can_format(device, prefs):
            return item.to_dictionary(device)