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
WAV_DIR = '/home/pi/wav_files'

i2c = busio.I2C(board.SCL, board.SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

p = pyaudio.PyAudio()
adev_list = []
mic_name = ['Blue','Logitech','USB PnP Sound Device'][0]
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

time_btw_tx  = 60
duration_min =120 
menu_state = 'Home'
last_time = timer()
failures = 0
update_display = True
menu_info = ''

# IP address
try:
    ip_addr= os.popen('hostname -I').read().split(' ')[0]
except:
    ip_addr = 'No IP'

row_buff = ['']*6
row_list = [0,11,22,33,44,55]
btn_list = ['Up','Down','Left','Right','A','B','C']

def nop():
    global menu_info
    print(menu_info)
def show_ip():
    global menu_info
    menu_info = ip_addr
    print(menu_info)
    

def show_rows():
    global update_display
    global menu_info

    print('show_rows ', menu_state)
    row_buff[0] = menu_state
    r = 1

    while r < 5:
        row_buff[r] = ''
        r=r+1
    r = 1
    i = 0
    
    while r < 5 and i < len(btn_list):
        s = menu_dict[menu_state][btn_list[i]][0]
        if s != '':
            row_buff[r] = btn_list[i] + ': ' + s
            r=r+1
        i=i+1
        
    row_buff[5] = menu_info
    
    #ip_addr
    # draw a box to clear the image
    display.fill(0)
    for i in range(len(row_list)):
        display.text(row_buff[i], 0, row_list[i], 1)
    display.show()

def shut_down():
    global menu_info
    menu_info = 'shutdown'
    print(menu_info)
    call("sudo shutdown -h now", shell=True)    

def reboot():
    global menu_info
    menu_info = "reboot"
    print(menu_info)
    call("sudo shutdown -r now", shell=True)

def copy_clip(file_name):
    print('copy_clip: ', file_name)
    try:
        p = subprocess.Popen(["scp", file_name, "tom@192.168.0.16:3d_audio"])
        sts = os.waitpid(p.pid, 0)
    except:
        failures = failures + 1
        print('scp failed')

def rec_audio_clip(clip_name):
    record_secs = 3
    wav_output_filename = WAV_DIR + '/' +clip_name+'.wav' # name of .wav file
    command = ["arecord","--device=hw:1,0",
                         "-d",str(record_secs),
                         "--format","S16_LE",
                         "--rate","44100",
                         "-c1",wav_output_filename]
    outp = subprocess.check_output(command, stdin=None, stderr=None,shell=False,universal_newlines=False)
    print(outp)
    copy_clip(wav_output_filename)
        
def rec_audio_clip_deprecated(clip_name):
    print('Recording')
    do_continue = True
    
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    record_secs = 3 # seconds to record
    dev_index = aindx # device index found by p.get_device_info_by_index(ii)
    wav_output_filename = WAV_DIR + '/' +clip_name+'.wav' # name of .wav file
    if do_continue:
        try:
            audio = pyaudio.PyAudio() # create pyaudio instantiation
        except:
            print('Failed to create a pyaudio instance')
            do_continue = False
    if do_continue:
        try:
            # create pyaudio stream
            stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)
            print("Audio Stream")
            frames = []
        except:
            print('Failed to create an audio stream')
            do_continue = False
    if do_continue:
        try:
            # loop through stream and append audio chunks to frame array
            for ii in range(0,int((samp_rate/chunk)*record_secs)):
                print(ii)
                data = stream.read(chunk)
                print(len(data))
                frames.append(data)
        except:
            print('failed when reading the stream')
            do_continue = False
    if do_continue:
        try:
            print("finished recording")
            # stop the stream, close it, and terminate the pyaudio instantiation
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except:
            print('failed when reading the stream')
            do_continue = False
    if do_continue:
        try:
            # save the audio frames as .wav file
            wavefile = wave.open(wav_output_filename,'wb')
            wavefile.setnchannels(chans)
            wavefile.setsampwidth(audio.get_sample_size(form_1))
            wavefile.setframerate(samp_rate)
            wavefile.writeframes(b''.join(frames))
            wavefile.close()
            copy_clip(wav_output_filename)
        except:
            do_continue = False
            print('Saving recorded data failed')
    if not do_continue:
        failures = failures + 1
         

 
def start_rec():
    global recording
    global menu_info
    recording = True
    menu_info = 'Start recording'
    
def stop_rec():
    global recording
    global menu_info
    recording = False
    menu_info = 'Stop recording'
    
def adjust_duration(t_min):
    global duration_min
    global menu_info

    duration_min = duration_min + t_min
    if duration_min < 0:
        duration_min = 0
    menu_info = 'Duration ' + str(duration_min) + ' min'    
    
def adjust_interval(t_sec):
    global time_btw_tx
    global menu_info
    
    time_btw_tx = time_btw_tx + t_sec
    if time_btw_tx < 0:
        time_btw_tx = 0
    menu_info = 'Interval ' + str(time_btw_tx) + ' sec'
def rec_main():
    global menu_info
    menu_info = str(duration_min) + 'min x ' + str(time_btw_tx) + 'sec'
    
    
# menu_dict  = { state_name: {*:[menu_name, next_state, callback_function]}}    

menu_dict = {
    'Home':       {'A':     ['','Close',nop],
                   'B':     ['','Close',nop],
                   'Up':    ['IP address','IP address',show_ip],
                   'Down':  ['Start','Start',rec_main],
                   'Left':  ['','Home',nop],
                   'Right': ['','Home',nop],
                   'C':     ['','Home',nop]},
    'Close':      {'A':     ['Shutdown','',shut_down],
                   'B':     ['Restart','',reboot],
                   'Up':    ['Home','Home',nop],
                   'Down':  ['','',nop],
                   'Left':  ['','',nop],
                   'Right': ['','',nop],
                   'C':     ['','',nop]},
    'Start':      {'A':     ['','Close',nop],
                   'B':     ['','Close',nop],
                   'Up':    ['Interval','Interval',lambda: adjust_interval(0)],
                   'Down':  ['Duration','Duration',lambda: adjust_duration(0)],
                   'Left':  ['Home','Home',nop],
                   'Right': ['','',nop],
                   'C':     ['Start','Running',start_rec]},
    'Duration':   {'A':     ['','Close',nop],
                   'B':     ['','Close',nop],
                   'Up':    ['Start','Start',rec_main],
                   'Down':  ['Interval','Interval',lambda: adjust_interval(0)],
                   'Left':  ['-10 min','',lambda: adjust_duration(-10)],
                   'Right': ['+10 min','',lambda: adjust_duration(10)],
                   'C':     ['','',nop]},
 
    'Interval':   {'A':     ['','Close',nop],
                   'B':     ['','Close',nop],
                   'Up':    ['Duration','Duration',lambda: adjust_duration(0)],
                   'Down':  ['Start','Start',rec_main],
                   'Left':  ['-Ival','',lambda: adjust_interval(-10)],
                   'Right': ['+Ival','',lambda: adjust_interval(10)],
                   'C':     ['','',nop]},
    'Running':    {'A':     ['','Close',nop],
                   'B':     ['','Close',nop],
                   'Up':    ['Interval','Interval',lambda: adjust_interval(0)],
                   'Down':  ['Duration','Duration',lambda: adjust_duration(0)],
                   'Left':  ['Stop','Start',stop_rec],
                   'Right': ['Start','',start_rec],
                   'C':     ['','',nop]},  
    'Ready':      {'A':     ['','Close',nop],
                   'B':     ['','Close',nop],
                   'Up':    ['','',nop],
                   'Down':  ['','',nop],
                   'Left':  ['','',nop],
                   'Right': ['','',nop],
                   'C':     ['','',nop]},
     'IP address': {'A':    ['','',nop],
                   'B':     ['','',nop],
                   'Up':    ['Close','Close',nop],
                   'Down':  ['Home','Home',nop],
                   'Left':  ['','',nop],
                   'Right': ['','',nop],
                   'C':     ['','',nop]}
}


def do_btn(btn_name):
    global menu_state
    global update_display
    global menu_info
    
    menu_info =''
    new_state = menu_dict[menu_state][btn_name][1]
    menu_dict[menu_state][btn_name][2]()
    
    print(menu_state,btn_name,'->',new_state)
    if new_state != '':
        menu_state = new_state
    update_display = True    

        
btn_A.when_pressed = lambda: do_btn('A')
btn_B.when_pressed = lambda: do_btn('B')
btn_Up.when_pressed = lambda: do_btn('Up')
btn_Down.when_pressed = lambda: do_btn('Down')
btn_Left.when_pressed = lambda: do_btn('Left')
btn_Right.when_pressed = lambda: do_btn('Right')
btn_Center.when_pressed = lambda: do_btn('C')

time1 = time.monotonic()
next_clip = time1 + time_btw_tx

print('main while loop')
while True:
    global update_display
    if time.monotonic() > time1 + 60:
        time1 = time1 + 60
        if duration_min > 0:
            duration_min = duration_min -1
    if recording:    
        if duration_min > 0:
            if time.monotonic() > time1:
                time1 = time1 + time_btw_tx
                ts = time.localtime()
                st = time.strftime("%Y-%m-%d_%H-%M-%S", ts)
                if recording:
                    try:
                        menu_info  = st
                        print(st)
                        rec_audio_clip(st)                     
                    except:
                        menu_info = 'Recording failed' 
                        print(menu_info)
                
                update_display = True
        else:
            recording = False
            menu_state = 'Ready'
            update_display = True     
    if update_display == True:
        show_rows()
        update_display = False
    if failures > 10:
        reboot()
    time.sleep(0.1)
