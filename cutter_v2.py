"""
Modified code from one of the ME-106 labs
"""

from machine import Pin, ADC
# import machine
import time

PIN_SPEAKER = Pin(21, Pin.OUT)
PIN_CUTTER = Pin(6, Pin.OUT)

PIN_CUTTER.off()
PIN_SPEAKER.off()

def main():
    pressure_check = adc_example()
    print("Pressure check pass: {}".format(pressure_check))
    if(not pressure_check):
        return False
    print("Cutting in 2 seconds...")
    PIN_SPEAKER.on()
    time.sleep(1)
    PIN_SPEAKER.off()
    PIN_CUTTER.on()
    time.sleep(0.05)
    PIN_CUTTER.off()
    time.sleep(1)
    print("Done cutting!")
    return True

def adc_example():
    # pot_read.py
    # import machine
    # import time
    # pot = machine.ADC(27)

    # 0 PSI = 0.3 V
    # 40 PSI = 1.1 V
    # 80 PSI = 1.9 V - 2.1 V?

    pot = ADC(27)
    min_pressure = 40 # psi
    # pot_values = []
    voltage_values = []
    for i in range(10):
    # while(True):
        # Or a while loop that waits until canister is pressurized
        pot_value = pot.read_u16()
        # pot_values.append(pot_value)
        volts = pot_value * 3.3 / 65535
        voltage_values.append(volts)
        # print("Pot value = {}\nEquivalent to {} V\n".format(pot_value, volts))
        print("Volts = {0:.3f}".format(volts))
        time.sleep(0.1)
    voltage_avg = sum(voltage_values) / len(voltage_values)
    print("Average voltage = {}".format(voltage_avg))
    return (voltage_avg > 1.1 and voltage_avg < 2.1)
    