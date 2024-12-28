from machine import Pin, SoftI2C, PWM
from time import sleep
import _thread, machine, time
import ssd1306

# This is a beat divider and quantizer designed for the Clackatronics Micro module
# Beat Divider: Gate in signals are counted and reproduced on Gate out depending on the value set by the top knob, from 1 to 1 to 1 to 16
# Quantizer: Select your scale with the lower knob and 1v/oct signals are changed to the nearest note on the scale
# Note the DAC on the micro isn't the best, so Quantization has a bit of a squeal on some notes. Can be musical...
# Supports an OLED display but runs fine if one isn't installed

gate_every = 2
scale_selection = "Major"

scales = [
    "Major",
    "Natural Minor",
    "Harmonic Minor",
    "Pentatonic",
    "Blues",
    "Dorian",
    "Mixolydian",
    "Chromatic",
    "Whole Tone",
    "Diminished"
]

scale_tones = {
    "Major": [0, 2, 4, 5, 7, 9, 11],  # C Major: C, D, E, F, G, A, B
    "Natural Minor": [0, 2, 3, 5, 7, 8, 10],  # A Minor: A, B, C, D, E, F, G
    "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11],  # A Harmonic Minor: A, B, C, D, E, F, G#
    "Pentatonic": [0, 2, 4, 7, 9],  # C Pentatonic: C, D, E, G, A
    "Blues": [0, 3, 5, 6, 7, 10],  # C Blues: C, E♭, F, F#, G, B♭
    "Dorian": [0, 2, 3, 5, 7, 9, 10],  # D Dorian: D, E, F, G, A, B, C
    "Mixolydian": [0, 2, 4, 5, 7, 9, 10],  # G Mixolydian: G, A, B, C, D, E, F
    "Chromatic": list(range(12)),  # All semitones in an octave
    "Whole Tone": [0, 2, 4, 6, 8, 10],  # C Whole Tone: C, D, E, F#, G#, A#
    "Diminished": [0, 2, 3, 5, 6, 8, 9, 11]  # C Octatonic: C, D, E♭, F, F#, G#, A, B
}

def task(n, delay):
    # this is a thread that runs on one of the two processors, updating the screen and LEDs and capturing knob values
    from machine import Pin, SoftI2C, PWM
    from time import sleep
    import _thread, machine, time
    import ssd1306

    global gate_every 
    global scale_selection
    prev_gate_setting = 0

    top_knob = machine.ADC(27)
    bottom_knob = machine.ADC(28) 

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
        if has_device and (prev_gate_setting != gate_every or prev_scale_selection != scale_selection):
            oled.fill(0)
            oled.text("Signal to Noise", 0, 0)
            for x in range(128):
                oled.pixel(x, 10, 1)

            oled.text("Divide/Quantize", 0, 20) 
            oled.text("Divide: 1-" + str(gate_every), 0, 35) 
            oled.text(scale_selection, 0, 50)
            oled.show()
            prev_gate_setting = gate_every
            prev_scale_selection = scale_selection

        gate_every = (top_knob.read_u16() * 15) // 65535 + 1 # this knob sets 1 to 16 beat divisions
        scale_selection = scales[(bottom_knob.read_u16() * 9) // 65535] # this knob selects the scale for quantization
        
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
    global gate_count
    
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

cv_in = machine.ADC(26)
cv_out = PWM(Pin(6))
cv_out.freq(100000)

def quantize_cv(input_cv, scale):
    # Convert input CV (0-65535) to voltage 
    input_voltage = (input_cv / 65535) * 5

    # Calculate the octave and position within the octave
    octave = int(input_voltage)
    position_in_octave = input_voltage - octave

    # Find the nearest note in the scale
    semitone = round(position_in_octave * 12)
    closest_note = min(scale, key=lambda note: abs(note - semitone))

    # Calculate the quantized voltage
    quantized_voltage = octave + (closest_note / 12)
    return quantized_voltage

def set_output_voltage(voltage):
    # Calculate the corresponding duty cycle (0 to 65535), value is inverted
    duty_cycle = int((1 - (voltage / 5)) * 65535)
    cv_out.duty_u16(duty_cycle)

while True:
    # quantizer
    input_cv = cv_in.read_u16()
   
   # Quantize the input CV
    quantized_voltage = quantize_cv(input_cv, scale_tones[scale_selection])

    # Output the quantized voltage
    set_output_voltage(quantized_voltage)

    # Small delay to prevent excessive CPU usage
    sleep(0.01)
    
        
        
        
