"""
Audio Sampler for 3D printing

Adafruit 128x64 Bonnet:
sudo pip3 install adafruit-circuitpython-ssd1306
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo i2cdetect -y 1
"""
import os
import subprocess
import board
# Import Python System Libraries
import time
from datetime import datetime
# Import Raspberry Libraries
from gpiozero  import Button
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw
import adafruit_ssd1306
import os
from timeit import default_timer as timer
from subprocess import call
import pyaudio
import wave

i2c = busio.I2C(board.SCL, board.SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

p = pyaudio.PyAudio()
adev_list = []
mic_name = ['Blue','Logitech'][1]
for ii in range(p.get_device_count()):
    adev_list = adev_list + [p.get_device_info_by_index(ii).get('name')]
print(adev_list)
#aindx_str = [i for i in adev_list if 'Logitech' in i][0]
aindx_str = [i for i in adev_list if mic_name in i][0]
aindx = adev_list.index(aindx_str)
print(aindx_str,aindx)




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

# 128x64 OLED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height
menu_state = 'Home'
recording = False

time_btw_tx  = 30
duration_min =120 
menu_state = 'Home'
last_time = timer()

# IP address
try:
    ip_addr= os.popen('hostname -I').read().split(' ')[0]
except:
    ip_addr = 'No IP'

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
        row_buff[5] = str(time_btw_tx) +' sec '+ str(duration_min) +' min'
    
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

def copy_clip(file_name):
    p = subprocess.Popen(["scp", file_name, "tom@192.168.0.10:3d_audio"])
    sts = os.waitpid(p.pid, 0)

def rec_audio_clip(clip_name):
    print('Recording')
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    record_secs = 3 # seconds to record
    dev_index = aindx # device index found by p.get_device_info_by_index(ii)
    wav_output_filename = clip_name+'.wav' # name of .wav file

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    copy_clip(wav_output_filename)

def start_rec():
    global recording
    recording = True
    
def stop_rec():
    global recording
    recording = False
    
def adjust_duration(t_min):
    global duration_min
    duration_min = duration_min + t_min
    if duration_min < 0:
        duration_min = 0
    
def adjust_interval(t_sec):
    global time_btw_tx
    time_btw_tx = time_btw_tx + t_sec
    if time_btw_tx < 0:
        time_btw_tx = 0
    
    

menu_dict = {
    'Home':       {'A':['Start Rec','Recording',start_rec],
                   'B':['Stop Rec','Home',stop_rec],
                   'U':['IP address','IP address',nop],
                   'D':['Shutdown','Shutdown',nop],
                   'L':['Home','Home',nop],
                   'R':['Home','Home',nop],
                   'C':['Home','Home',nop]},
    'Shutdown':   {'A':['Shutdown','Home',shut_down],
                   'B':['Restart','Home',reboot],
                   'U':['Home','Home',nop],
                   'D':['Home','Home',nop],
                   'L':['Home','Home',nop],
                   'R':['Home','Home',nop],
                   'C':['Home','Home',nop]},
    'Recording':  {'A':['Home','Home',shut_down],
                   'B':['Stop Recording','Home',stop_rec],
                   'U':['+10 min','Recording',lambda: adjust_duration(10)],
                   'D':['-10 min','Recording',lambda: adjust_duration(-10)],
                   'L':['-Ival','Recording',lambda: adjust_interval(-10)],
                   'R':['+Ival','Recording',lambda: adjust_interval(10)],
                   'C':['Home','Home',nop]},
    'IP address': {'A':['Home','Home',nop],
                   'B':['Home','Home',nop],
                   'U':['Home','Home',nop],
                   'D':['Home','Home',nop],
                   'L':['Home','Home',nop],
                   'R':['Home','Home',nop],
                   'C':['Home','Home',nop]}
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

time1 = time.monotonic()
next_clip = time1 + time_btw_tx
while True:

    if time.monotonic() > time1 + 60:
        time1 = time1 + 60
        duration_min = duration_min -1
    if duration_min > 0:
        if time.monotonic() > time1:
            time1 = time1 + time_btw_tx
            ts = time.gmtime()
            st = time.strftime("%Y-%m-%d_%H-%M-%S", ts)
            if recording:
                try:
                    rec_audio_clip(st)
                except:
                    print('Recording failed')
            print(st)

            

    show_rows()
    time.sleep(0.1)
