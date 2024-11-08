import os
import sys
from typing import List, Dict, Any

import usb
import yaml
from evdev import UInput, ecodes, AbsInfo


path = os.path.join(os.path.dirname(__file__), "config.yaml")
# Loading tablet configuration
with open(path, "r") as f: config = yaml.load(f, Loader=yaml.FullLoader)

def convert_codes(target: List[str]) -> List[int]:
    temp = []
    for t in target: temp.extend([ecodes.ecodes[x] for x in t.split("+")])
    return temp

def setEvents(target: List[int]) -> Dict[int, List[Any]]:
    if target == btn_codes: return {ecodes.EV_KEY: btn_codes}
    return {
        ecodes.EV_KEY: pen_codes,
        ecodes.EV_ABS: [
            (ecodes.ABS_X, AbsInfo(0, 0, config["pen"]["max_x"], 0, 0, config["pen"]["resolution_x"])),         
            (ecodes.ABS_Y, AbsInfo(0, 0, config["pen"]["max_y"], 0, 0, config["pen"]["resolution_y"])),
            (ecodes.ABS_PRESSURE, AbsInfo(0, 0, config["pen"]["max_pressure"], 0, 0, 0))
        ],
    }

# Subtitle is indicated if the devices >= 2
def setUInput(any_events: Dict[int, List[Any]], subtitle: str) -> UInput:
    return UInput(events=any_events, name=config["xinput_name"] + subtitle, version=0x3)

def coordinate_axis(axis: str) -> int:
    return config["pen"]["max_" + axis] * config["settings"]["swap_direction_" + axis]

# Get the required ecodes from configuration
pen_codes = []
btn_codes = []
for k, v in config["actions"].items():
    codes = btn_codes if k == "tablet_buttons" else pen_codes
    if isinstance(v, list): codes.extend(v)
    else: codes.append(v)

pen_codes = convert_codes(pen_codes)
btn_codes = convert_codes(btn_codes)

# Find the device
dev = usb.core.find(idVendor=config["vendor_id"], idProduct=config["product_id"])
# Interface [0] refers to mass storage
# Interface [1] does not reac in any way
# Select end point for reading second interface [2] for actual data
# FIXME: I couldn't find a stylus in the interface [2]. In the documentation it is present in interface [1], but it is not supported
ep = dev[0].interfaces()[2].endpoints()[0]
# Reset the device (don't know why, but till it works don't touch it)
dev.reset()

# Drop default kernel driver from all devices
for i in [0, 1, 2]:
    if dev.is_kernel_driver_active(i): dev.detach_kernel_driver(i)

# Set new configuration
dev.set_configuration()

vpen = setUInput(setEvents(pen_codes), "")
vbtn = setUInput(setEvents(btn_codes), "_buttons")

# Direction and axis configuration
max_x = coordinate_axis("x")
max_y = coordinate_axis("y")
x1, x2, y1, y2 = (3, 2, 5, 4) if config["settings"]["swap_axis"] else (5, 4, 3, 2)

pressed = -1

if __name__ == "__main__":
    while True:
        try:
            data = dev.read(ep.bEndpointAddress, ep.wMaxPacketSize)
            if data[1] in [192, 193]: # Pen actions
                pen_x = abs(max_x - (data[x1] * 255 + data[x2]))
                pen_y = abs(max_y - (data[y1] * 255 + data[y2]))
                pen_pressure = data[7] * 255 + data[6]
                vpen.write(ecodes.EV_ABS, ecodes.ABS_X, pen_x)
                vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, pen_y)
                vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, pen_pressure)
                if data[1] == 192: vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
                else: vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 1)
            elif data[0] == 2: # Tablet button actions
                press_type = 1
                if data[3] == 86: pressed = 0
                elif data[3] == 87: pressed = 1
                elif data[3] == 47: pressed = 2
                elif data[3] == 48: pressed = 3
                elif data[3] == 43: pressed = 4
                elif data[3] == 44: pressed = 5
                else: press_type = 0
                key_codes = config["actions"]["tablet_buttons"][pressed].split("+")
                for key in key_codes:
                    act = ecodes.ecodes[key]
                    vbtn.write(ecodes.EV_KEY, act, press_type)
            # Flush
            vpen.syn()
            vbtn.syn()
        except usb.core.USBError as e:
            if e.args[0] == 19:
                vpen.close()
                raise Exception("Device has been disconnected")
        except KeyboardInterrupt:
            vpen.close()
            vbtn.close()
            sys.exit("\nDriver terminated successfully")
