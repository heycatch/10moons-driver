# 10moons-driver

## SZ PING-IT INC. [T605] Driver Inside Tablet
![](https://raw.githubusercontent.com/heycatch/10moons-driver/refs/heads/master/T605.png)

Simple driver for 10moons T605 tablet for linux

## About

Driver which provides basic functionality for 10moons T605 tablet:
* 6 buttons on the tablet itself (1: zoomout; 2: zoomin; 3: brush; 4: fill; 5: ctrl+z; 6: panning)
* 2 buttons on the stylus (1(+): increase brush size; 2(-): reduce brush size) [READ FIXME](https://github.com/heycatch/10moons-driver-t605/blob/d70e474fbdcef673c9ed62f68df44e5ca5ed1e15/driver.py#L53)
* Correct X and Y positioning
* Pressure sensitivity

Tablet has 4096 levels in both axes and 2047 levels of pressure.

## How to use

Clone or download this repository.

```
git clone https://github.com/heycatch/10moons-driver-t605.git
```

Then install all dependencies listed in _requirements.txt_ file either using python virtual environments or not.

```
python -m pip install -r requirements.txt
```

Connect tablet to your computer and then run _driver.py_ file with sudo privileges.

```
sudo python driver.py
```

**You need to connect your tablet and run the driver prior to launching a drawing software otherwise the device will not be recognized by it.**

## Configuring tablet

Configuration of the driver placed in _config.yaml_ file.

You may need to change the *vendor_id* and the *product_id* but I'm not sure (You device can have the same values as mine, but if it is not you can run the *lsusb* command to find yours).

Buttons assigned from in the order from left to right. You can assign to them any button on the keyboard and their combinations separating them with a plus (+) sign.

If you find that using this driver with your tablet results in reverse axis or directions (or both), you can modify parameters *swap_axis*, *swap_direction_x*, and *swap_direction_y* by changing false to true and another way around.

To list all the possible key codes you may run:
```
python -c "from evdev import ecodes; print([x for x in dir(ecodes) if 'KEY' in x])"
```