import time
from machine import Pin, I2C
from vl53l0x_v1 import VL53L0X
# from vl53l0x_v2 import VL53L0X

def main(scan_bool):
    if(not scan_bool):
        return False
    print("setting up i2c")
    sda = Pin(0)
    scl = Pin(1)
    id = 0
    # id = 1

    i2c = I2C(id=id, sda=sda, scl=scl)

    print(i2c.scan())
    # time.sleep(1)
    time.sleep(0.1)

    # print("creating vl53lox object")
    # Create a VL53L0X object
    # tof = VL53L0X(i2c)
    tof = VL53L0X(i2c)

    # Pre: 12 to 18 (initialized to 14 by default)
    # Final: 8 to 14 (initialized to 10 by default)

    # the measuting_timing_budget is a value in ms, the longer the budget, the more accurate the reading. 
    budget = tof.measurement_timing_budget_us
    print("Budget was:", budget)
    tof.set_measurement_timing_budget(40000)

    # Sets the VCSEL (vertical cavity surface emitting laser) pulse period for the 
    # given period type (VL53L0X::VcselPeriodPreRange or VL53L0X::VcselPeriodFinalRange) 
    # to the given value (in PCLKs). Longer periods increase the potential range of the sensor. 
    # Valid values are (even numbers only):

    # tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 12)

    # tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 8)

    #while True:
    ranges = []
    wire_inside = False
    for i in range(10):
        # Start ranging
        # print(tof.ping()-50, "mm")
        if(i > 1):
            # skipping first range, useless value, always 8191
            print(tof.ping(), "mm")
        ranges.append(int(tof.ping()))
    ranges.pop(0)
    ranges_sum = sum(ranges)
    ranges_avg = ranges_sum / len(ranges)
    if(ranges_avg < 60):
        wire_inside = True
    print("Average range = {} mm".format(ranges_avg))
    return wire_inside

def stop():
    # print("Stopping ToF scan.")
    pass

# main()