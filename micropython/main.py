from machine import Pin, SoftI2C, PWM
from time import sleep
import _thread, machine, time
import ssd1306

# This is a beat divider designed for the Clackatronics Micro module
# Gate in signals are counted and reproduced on Gate out depending on the value set by the top knob, from 1 to 1 to 1 to 16
# Supports an OLED display but runs fine if one isn't installed

gate_every = 2

def task(n, delay):
    # this is a thread that runs on one of the two processors, updating the screen and LEDs and capturing knob values
    from machine import Pin, SoftI2C, PWM
    from time import sleep
    import _thread, machine, time
    import ssd1306

    global gate_every 
    prev_gate_setting = 0

    top_knob = machine.ADC(27) 

    i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
    devices = i2c.scan()
    has_device = False

    # This only works if you have an SSD1306 connected to the headers provided, but works fine if you don't
    if len(devices) == 0:
        print("No i2c device !")
    else:
        print('i2c devices found:', len(devices))
        for device in devices:
            print("I2C hexadecimal address: ", hex(device))
        has_device = True
        oled_width = 128
        oled_height = 64
        oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

    while True:
        if has_device and prev_gate_setting != gate_every:
            oled.fill(0)
            oled.text("Signal To Noise", 0, 0)
            for x in range(128):
                oled.pixel(x, 10, 1)

            oled.text("Beat Divider", 0, 20) 
            oled.text("Divide: 1-" + str(gate_every), 0, 35) 
            
            oled.show()
            prev_gate_setting = gate_every

        gate_every = (top_knob.read_u16() * 15) // 65535 + 1

        sleep(.1)


_thread.start_new_thread(task, (10, 0.5))

gate_in = Pin(2, Pin.IN, Pin.PULL_UP)
gate_on = False
gate_was_on = gate_in.value()
gate_count = 0

gate_out = Pin(5, Pin.OUT)

right_led = Pin(4, Pin.OUT)
left_led = Pin(3, Pin.OUT)

def irq_handle(pin):
    global gate_on
    
    # value is inverted
    if not pin.value():
        gate_on = True
        left_led.value(1)
        
        gate_count += 1

        # repeat if it's the right interval
        if gate_count >= gate_every:
            gate_count = 0
            # value is inverted
            gate_out.value(0)
            right_led.value(1)
    else:
        gate_on = False
        left_led.value(0)
        # value is inverted
        gate_out.value(1)
        right_led.value(0)

gate_in.irq(handler=irq_handle, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)

while True:
    # We can do other things here
    # future functionality incoming
   
    sleep(1)
        
        
        
