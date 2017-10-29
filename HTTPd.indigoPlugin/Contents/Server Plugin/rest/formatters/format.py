import unknown
import dimmer

formatter_list = [dimmer.Dimmer(), unknown.Unknown()]
def format_device(device):
    for item in formatter_list:
        if item.can_format(device):
            return item.to_dictionary(device)