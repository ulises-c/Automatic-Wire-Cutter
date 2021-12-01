from machine import Pin
from time    import sleep
import math

# encoder info
# 10 pulses per rev
# 32 mm per rev = 1.259843 inches
# x inches = y revolutions
# length/rev = 1.256/1
# rev = length/1.256
# if (count >= (length*10)/1.256): -> exit loop

# ENCODER STUFF
PIN_ENCA = 4
PIN_ENCB = 5
count = 0
old_count = 0
# cnt = 0
cnt_check = 0
pinA = Pin(PIN_ENCA, Pin.IN)
pinB = Pin(PIN_ENCB, Pin.IN)

def irq_a(pin):
    global count
    count += 1 if pinB.value() else -1

pinA.irq(trigger=Pin.IRQ_RISING, handler=irq_a)

# MOTOR STUFF
PIN_STEP = Pin(26, Pin.OUT)
PIN_DIRECTION = Pin(22, Pin.OUT)
STEP_ANGLE = 1.8
STEPS_PER_REV = 360 / STEP_ANGLE
STEPDELAY_USECS = 1
PIN_DIRECTION.off()

def steps(step_count, delay_usecs=STEPDELAY_USECS):
    '''Take 'count' steps clockwise (negative for counter-clockwise),
    pausing between steps for 'delay_usecs' microseconds'''
    abscount = abs(step_count) * 2
    if(step_count < 0):
        PIN_DIRECTION.on()
    else:
        PIN_DIRECTION.off()
    for i in range(abscount):
        PIN_STEP.toggle()
        sleep(delay_usecs/1000)
        # check_count()

def check_count():
    global cnt, old_count, cnt_check
    cnt = count
    old_count = cnt
    cnt_check += cnt
    print("cnt = {} | delta = {} | cnt_check = {} | count = {}".format(cnt, old_count-cnt, cnt_check, count))

def main(cut_len):
    # print("(Encoder) Length to cut = {}".format(cut_len))
    # length = 10 #in
    # length = cut_len
    pulses = (cut_len * 10) / (1.256)
    pulses = math.ceil(pulses)
    correction_factor = 1.042
    steps2do = cut_len * 200 / 1.256 * correction_factor
    print("Target pulses = {}".format(pulses))
    print("Feeding wire...")
    # while(abs(count) < pulses):
    #     steps(10*STEPS_PER_REV, STEPDELAY_USECS)
    #     check_count()
    steps(steps2do)
    print("Done feeding wire")
    return 1