"""
Audio Sampler for 3D printing
"""
import board
# Import Python System Libraries
import time
# Import Raspberry Libraries
from gpiozero  import Button
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull

from PIL import Image, ImageDraw
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x
import os
from timeit import default_timer as timer
# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)



io_pin = {'Btn_A':5,'Btn_B':6,'Btn_Left':27,'Btn_Right':23,'Btn_Up':17,'Btn_Down':22,'Btn_Center':4,}
btn_A = Button(io_pin['Btn_A'])
btn_B = Button(io_pin['Btn_B'])
btn_Left = Button(io_pin['Btn_Left'])
btn_Rigth = Button(io_pin['Btn_Right'])
btn_Up = Button(io_pin['Btn_Up'])
btn_Down = Button(io_pin['Btn_Down'])
btn_Center = Button(io_pin['Btn_Center'])


# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height


# IP address
try:
    ip_addr= os.popen('hostname -I').read().split(' ')[0]
except:
    ip_addr = 'No IP'

# menu_state = 'Initial State'

def nop():
    pass
def show_ip():
    row_buff[0] = ip_addr
    row_buff[1] = ''
    pass

menu_dict = {
    'Home':       {'A':['Show IP Address','IP Address',show_ip],
                   'B':['Send Data','Send',nop],
                   'U':['Home','Home',nop]},
    'IP Address': {'A':['','Home',show_ip],
                   'B':['','Home',nop],
                   'U':['Home','Home',nop]},
    'Send':       {'A':['Send msg A','Sending',nop],
                   'B':['Send msg B','Sending',nop],
                   'U':['Return home','Home',nop]},
    'Sending':    {'A':['','Home',nop],
                   'B':['','Home',nop],
                   'U':['Return home','Home',nop]},
}

def do_btn_A():
    global menu_state
    new_state = menu_dict[menu_state]['A'][1]
    menu_dict[menu_state]['A'][2]()
    menu_state = new_state

def do_btn_B():
    global menu_state
    new_state = menu_dict[menu_state]['B'][1]
    menu_dict[menu_state]['B'][2]()
    menu_state = new_state

def do_btn(btn_name):
    global menu_state
    new_state = menu_dict[menu_state]['btn_name'][1]
    menu_dict[menu_state]['btn_bame'][2]()
    menu_state = new_state

btn_A.when_pressed = do_btn_A
btn_B.when_pressed = do_btn_B
btn_Up.when_pressed = do_btn('U')

time_btw_tx = 10
menu_state = 'Home'
last_time = timer()
row_buff = ['','','']
row_list = [0,12,24]
btn_list = ['A','B','U']
while True:
    now_time = timer()
    if ( now_time -last_time ) >  time_btw_tx:
        last_time =  last_time + time_btw_tx
        print(now_time)

    packet = None
    # draw a box to clear the image
    display.fill(0)
    for i in range(len(row_list)):
        txt0 = menu_dict[menu_state][btn_list[i]][0]
        if txt0 == '':
            txt = row_buff[i]
        else:
            txt = btn_list[i] + ': ' + txt0
        display.text(txt, 0, row_list[i], 1)

    display.show()
    time.sleep(0.1)
