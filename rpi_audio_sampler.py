"""
Audio Sampler for 3D printing

Adafruit 128x64 Bonnet:
sudo pip3 install adafruit-circuitpython-ssd1306
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo i2cdetect -y 1
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

import os
from timeit import default_timer as timer
from subprocess import call

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)



io_pin = {'Btn_A':6,'Btn_B':5,'Btn_Left':27,'Btn_Right':23,'Btn_Up':17,'Btn_Down':22,'Btn_Center':4,}
btn_A = Button(io_pin['Btn_A'])
btn_B = Button(io_pin['Btn_B'])
btn_Left = Button(io_pin['Btn_Left'])
btn_Right = Button(io_pin['Btn_Right'])
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
menu_state = 'Home'
row_buff = ['']*8

# IP address
try:
    ip_addr= os.popen('hostname -I').read().split(' ')[0]
except:
    ip_addr = 'No IP'

# menu_state = 'Initial State'

row_buff = ['']*6
row_list = [0,11,22,33,44,55]
btn_list = ['A','B','U','D','L','R','C']

def nop():
    pass

def show_rows():
    row_buff[0] = menu_state+':'
    row_buff[1] = 'Up  : '+ menu_dict[menu_state]['U'][0]
    row_buff[2] = 'Down: '+ menu_dict[menu_state]['D'][0]
    if menu_state == 'IP address':
        row_buff[3] = 'IP: '+ip_addr
    else:   
        row_buff[3] = 'A: '+menu_dict[menu_state]['A'][0]
        row_buff[4] = 'B: '+menu_dict[menu_state]['B'][0]
        row_buff[5] = 'Row5'
    
    ip_addr
    # draw a box to clear the image
    display.fill(0)
    for i in range(len(row_list)):
        display.text(row_buff[i], 0, row_list[i], 1)
    display.show()

def shut_down():
    call("sudo shutdown -h now", shell=True)    

def reboot():
    call("sudo shutdown -r now", shell=True)    

menu_dict = {
    'Home':       {'A':['Home','Home',nop],
                   'B':['Home','Home',nop],
                   'U':['IP address','IP address',nop],
                   'D':['Shutdown','Shutdown',nop],
                   'L':['Home','Home',nop],
                   'R':['Home','Home',nop],
                   'C':['Home','Home',nop]},
    'Shutdown':   {'A':['Shutdown','Shutdown',shut_down],
                   'B':['Restart','Shutdown',reboot],
                   'U':['Home','Home',nop],
                   'D':['Home','Home',nop],
                   'L':['Home','Home',nop],
                   'R':['Home','Home',nop],
                   'C':['Home','Home',nop]},
    'IP address': {'A':['Home','Home',nop],
                   'B':['Home','Home',nop],
                   'U':['Return home','Home',nop],
                   'D':['Home','Home',nop],
                   'L':['Home','Home',nop],
                   'R':['Home','Home',nop],
                   'C':['Home','Home',nop]},
    'Sending':    {'A':['','Home',nop],
                   'B':['','Home',nop],
                   'U':['Return home','Home',nop],
                   'D':['Home','Home',nop],
                   'L':['Home','Home',nop],
                   'R':['Home','Home',nop],
                   'C':['Home','Home',nop]},
}


def do_btn(btn_name):
    global menu_state
    new_state = menu_dict[menu_state][btn_name][1]
    menu_dict[menu_state][btn_name][2]()
    menu_state = new_state

btn_A.when_pressed = lambda: do_btn('A')
btn_B.when_pressed = lambda: do_btn('B')
btn_Up.when_pressed = lambda: do_btn('U')
btn_Down.when_pressed = lambda: do_btn('D')
btn_Left.when_pressed = lambda: do_btn('L')
btn_Right.when_pressed = lambda: do_btn('R')
btn_Center.when_pressed = lambda: do_btn('C')

time_btw_tx = 10
menu_state = 'Home'
last_time = timer()

while True:
    now_time = timer()
    if ( now_time -last_time ) >  time_btw_tx:
        last_time =  last_time + time_btw_tx
        print(now_time)

    show_rows()
    time.sleep(0.1)
