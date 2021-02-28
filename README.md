# Camera peace

![Screencapture of using Camera peace](screencapture.gif)

A little script to manipulate your webcam in real time for video calls. 
Gives you peace of mind, the ability to sneak away to make coffee, zoom off, or freedom to mind wander without looking absent. 
¯\\\_(ツ)\_/¯

~~It captures an avatar of you in real time and then synthesizes a credible, interactive version of you using 
state of the art artificial intelligence models.~~
It allows you to freeze or loop yourself. Stutter and artifact utilities help convey that you are having a bad 
connection and masks the not-really-looping loop you just created.

Also, don't take this too serious and don't forget that 
[there are no technological solutions for social problems](https://media.ccc.de/v/36c3-10988-wohnungsbot_an_automation-drama_in_three_acts). 

## How to

Launch this script before joining the video call. 
Then simply select the 'Dummy output' camera when joining the call.
Control the different modes from the terminal window. 
Shortcuts are presented on screen in blue.

## Requirements
Probably only runs on Linux (tested with Ubuntu 20.04), with Python 3.x (tested with 3.7).

## Setup
You might need to install more/other packages! Using a virtual environment might also be a good idea.
 ```shell
sudo apt install v4l2loopback-utils
pip3 install --user opencv-python pyfakewebcam
 ```

Create a fake webcam before running the script:
```shell
sudo modprobe v4l2loopback devices=1 exclusive_caps=1
```
(`exclusive_caps` is required for the fake webcam to show up in the browser.)

## Development

Uses [black](https://github.com/psf/black) for formatting.

## To-do

- Support other platforms
- Audio manipulation

---

Inspiration: https://stackoverflow.com/a/61394280  
See also: http://signalculture.org/interstream.html