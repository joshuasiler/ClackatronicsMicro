This is project is designed to run on a Clackactronics Micro module, based on the Raspberry Pi. Learn more at https://clacktronics.co.uk/byom/

Currently this software enables a Beat Divider, which accepts a clock into Gate In and reproduces it to Gate Out at an interval set by the top knob, from 1:1 to 1:16. This can be connected to the LFO or any other clock source, like a sequencer, to create interleaved sounds. Future functionality is planned. 

To install, holding the boot button while connecting your module to USB. Your computer will then mount the module as a drive. Drag the firmware.uf2 file into the new drive. The module 
will then reboot and is ready to run. 

It supports the Micro module as built, and also includes display code if you attach an SSD1306 OLED display to your module using the included headers. 

Also included are development resources, including the micropython runtime, SDK documentation and Python files. These are not necessary unless you wish to modify the code yourself.

Author: Joshua Siler, Signal to Noise Audio, 2024