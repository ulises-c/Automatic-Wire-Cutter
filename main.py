# Pico LCD 1.14
# https://www.waveshare.com/wiki/Pico-LCD-1.14

from machine import Pin,SPI,PWM
import framebuf
import time
import sys
# project files
import encoder_v3
import cutter_v2
import tof_sensor

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

stage = 0
stage_titles = ["Boot up stage", "User input stage", "Data confirmation stage", "ToF check stage", "Activating motor stage (display)", "Activating motor stage", "Wire cutting stage (display)", "Wire cutting stage", "Done", "Actually done"]
MAX_STAGE = 8
stage5_flash = True

class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 135
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff
        self.black =   0x0000
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x28)
        self.write_data(0x01)
        self.write_data(0x17)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x35)
        self.write_data(0x00)
        self.write_data(0xBB)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

def change_index(list, index, positive):
    if(stage != 1):
        return index
    if(positive == True):
        index += 1
    else:
        index -= 1

    if(index > len(list)-1):
        index = 0
    elif(index < 0):
        index = len(list) - 1
    return index

def stage_modify(stage, num):
    # print("Stage mod num = {}".format(num))
    if(num == 0):
        return stage
    stage += num
    if(stage < 0):
        stage = 0
    if(stage > MAX_STAGE):
        stage = 0
    print("\nStage = {}, {}".format(stage, stage_titles[stage]))
    return stage

def modify_value(list, index, positive):
    if(stage != 1):
        return
    if(positive == True):
        list[index] += 1
    else:
        list[index] -= 1

    if(list[index] < 0):
        list[index] = 9
    elif(list[index] > 9):
        list[index] = 0

def list2string(list):
    num_str = ''
    for num in list:
        num_str += str(num)
    return num_str

def list2float(list):
    number = 0
    number += list[0] * 10
    number += list[1]
    number += list[2] / 10
    return number

def display_blue_box():
    LCD.hline(5,5,230,LCD.blue)
    LCD.hline(5,130,230,LCD.blue)
    LCD.vline(5,5,125,LCD.blue)
    LCD.vline(235,5,125,LCD.blue)

def display_defaults():
    pass

def button_press(length_arr, amount, list_index, stage):
    if(keyA.value() == 0): # A
        LCD.fill_rect(208,12,20,20,LCD.red)
        stage = stage_modify(stage, 1)
    else :
        LCD.fill_rect(208,12,20,20,LCD.white)
        LCD.rect(208,12,20,20,LCD.red)
        
    if(keyB.value() == 0): # B
        LCD.fill_rect(208,103,20,20,LCD.red)
        stage = stage_modify(stage, -1)
    else :
        LCD.fill_rect(208,103,20,20,LCD.white)
        LCD.rect(208,103,20,20,LCD.red)

    if(key2.value() == 0): # UP
        LCD.fill_rect(37,35,20,20,LCD.red)
        modify_value(length_arr, list_index, True)
    else :
        LCD.fill_rect(37,35,20,20,LCD.white)
        LCD.rect(37,35,20,20,LCD.red)

    if(key5.value() == 0): # DOWN
        LCD.fill_rect(37,85,20,20,LCD.red)
        modify_value(length_arr, list_index, False)
    else :
        LCD.fill_rect(37,85,20,20,LCD.white)
        LCD.rect(37,85,20,20,LCD.red)
        
    if(key4.value() == 0): # LEFT
        LCD.fill_rect(12,60,20,20,LCD.red)
        list_index = change_index(length_arr, list_index, False)
    else :
        LCD.fill_rect(12,60,20,20,LCD.white)
        LCD.rect(12,60,20,20,LCD.red)
        
    if(key6.value() == 0): # RIGHT
        LCD.fill_rect(62,60,20,20,LCD.red)
        list_index = change_index(length_arr, list_index, True)
    else :
        LCD.fill_rect(62,60,20,20,LCD.white)
        LCD.rect(62,60,20,20,LCD.red)

    if(key3.value() == 0): # CENTER
        LCD.fill_rect(37,60,20,20,LCD.red)
    else :
        LCD.fill_rect(37,60,20,20,LCD.white)
        LCD.rect(37,60,20,20,LCD.red)
    
    amount = length_arr[3]
    return length_arr, amount, list_index, stage

def display_text(stage):
    if(stage == 0):
        # LCD = LCD_1inch14()
        #color BRG
        LCD.fill(LCD.white)
        LCD.text("Raspberry Pi Pico",10,10,LCD.red)
        LCD.text("PicoGo",10,30,LCD.green)
        LCD.text("Pico-LCD-1.14",10,50,LCD.blue)
        LCD.text("Spartan Racing - F21 ME106", 10, 70, LCD.black)
        LCD.text("Ulises Chavarria", 10, 90, LCD.black)
        LCD.text("Josue Garcia", 10, 100, LCD.black)
        LCD.text("Francis Supnet", 10, 110, LCD.black)
        LCD.fill_rect(208,12,20,20,LCD.white)
        LCD.text("Next", 174, 14, LCD.blue)
        LCD.rect(208,12,20,20,LCD.red)
    else:
        length_float = list2float(length_arr)
        LCD.text("Length = {0:.1f} in".format(length_float),85,80,LCD.black)
        LCD.text("Amount = {}".format(amount),85,100,LCD.black)
        LCD.text("Next", 174, 14, LCD.blue)
        LCD.text("Back", 174, 115, LCD.blue)

    if(stage == 1):
        LCD.text("Index = {}".format(list_index),85,40,LCD.black)
        LCD.text("Length = {} in".format(length_arr[:3]),85,60,LCD.black)
        # LCD.text("Length = {} in".format(length_str),85,80,LCD.black)
        display_index()
    
    elif(stage == 2):
        LCD.text("Confirm values", 85, 40, LCD.black)
    
    elif(stage == 3):
        LCD.text("Checking ToF", 85, 40, LCD.black)

    elif(stage == 4):
        LCD.text("Activating motor", 85, 40, LCD.black)
    
    elif(stage == 6):
        global stage5_flash
        if(stage5_flash):
            LCD.fill(LCD.red)
            stage5_flash = False
        elif(not stage5_flash):
            LCD.fill(LCD.white)
            stage5_flash = True
        
        LCD.text("CAUTION!!!", 85, 40, LCD.black)
        LCD.text("Cutting wire", 85, 60, LCD.black)
        LCD.text("CAUTION!!!", 85, 80, LCD.black)

    elif(stage == 8):
        LCD.fill(LCD.green)
        LCD.text("Done", 85, 20, LCD.black)
        LCD.text("Return", 160, 14, LCD.blue)
        LCD.fill_rect(208,12,20,20,LCD.white)
        LCD.rect(208,12,20,20,LCD.red)
        
def display_index():
    x = 140
    y = 55
    if(stage == 1):
        if(list_index == 0):
            x += 20
        elif(list_index == 1):
            x += 42
        elif(list_index == 2):
            x += 64
        elif(list_index == 3):
            # Fill this out for 3rd index, amount
            x = 150
            y = 95
        LCD.rect(x, y, 23, 18, LCD.blue)

if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768) # max 65535

    LCD = LCD_1inch14()
    # display_initial()

    keyA = Pin(15, Pin.IN, Pin.PULL_UP) # A
    keyB = Pin(17, Pin.IN, Pin.PULL_UP) # B
    key2 = Pin(2, Pin.IN, Pin.PULL_UP)  # UP
    key3 = Pin(3, Pin.IN, Pin.PULL_UP)  # CENTER
    key4 = Pin(16, Pin.IN, Pin.PULL_UP) # LEFT
    key5 = Pin(18, Pin.IN, Pin.PULL_UP) # DOWN
    key6 = Pin(20, Pin.IN, Pin.PULL_UP) # RIGHT

    # DEFAULT VALUES
    length_arr = [0, 0, 0, 1]
    amount = length_arr[3]
    list_index = 0
    length_float = list2float(length_arr)
    display_wait = 5
    stage = stage_modify(stage, 0)
    wire_inside = False
    check_tof = True

    while(True):
        LCD.fill(LCD.white)
        LCD.rect(84, 35, 145, 60, LCD.white)
        LCD.fill_rect(84, 35, 145, 60, LCD.white)
        LCD.fill_rect(150, 95, 23, 18, LCD.white)
        display_blue_box()
        length_arr, amount, list_index, stage = button_press(length_arr, amount, list_index, stage)
        length_float = list2float(length_arr)
        display_text(stage)
        LCD.show

        if(stage == 0):
            pass

        elif(stage == 1):
            # User input stage
            pass

        # if(amount < 1 and stage == 4):
        #     print("Cut amount was less than 1")
        #     # stage = 1
        #     pass

        elif(stage == 2):
            # User confirmation stage
            if(not check_tof):
                stage = stage_modify(stage, 0)
            check_tof = True
            pass

        elif(stage == 3):
            # Checking ToF stage
            wire_inside = tof_sensor.main(check_tof)
            check_tof = False
            tof_sensor.stop()
            if(wire_inside):
                stage = stage_modify(stage, 1)
            else:
                LCD.fill(LCD.red)
                LCD.text("No wire detected", 85, 60, LCD.black)
                LCD.show()
                time.sleep(0.5)
                stage = stage_modify(stage, -1)
            pass

        elif(stage == 4):
            # Activating motor stage (DISPLAY)
            # print("(Main) Length to cut = {}".format(length_float))
            if(display_wait > 0):
                display_wait -= 1
            elif(display_wait <= 0):
                display_wait = 10
                stage = stage_modify(stage, 1)
            pass

        elif(stage == 5):
            # Activating motor stage
            stage_setter = encoder_v3.main(length_float)
            stage = stage_modify(stage, 1)

        elif(stage == 6):
            # Wire cutting stage (DISPLAY)
            if(display_wait > 0):
                display_wait -= 1
            elif(display_wait <= 0):
                display_wait = 10
                # stage += 1
                stage = stage_modify(stage, 1)
            pass

        elif(stage == 7):
            # Wire cutting stage
            cutting_done = cutter_v2.main()
            if(cutting_done):
                length_arr[3] -= 1 # decreasing amount by 1
            if(amount > 1 and cutting_done):
                # stage = 3
                check_tof = True
                stage = stage_modify(stage, -4)
            elif(amount == 1 and cutting_done):
                # stage = 8
                stage = stage_modify(stage, 1)
            else:
                print("Did not pass pressure check... Retrying...")
                stage = stage_modify(stage, 0)
        
        elif(stage == 8):
            # Done stage
            pass
            
        else:
            print("Stage changed.\nNothing in this stage yet\nExiting...")
            # sys.exit()
            stage = 1

        LCD.show()
        time.sleep(0.1)
    # return amount, length_float