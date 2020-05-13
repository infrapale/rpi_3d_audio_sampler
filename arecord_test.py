import os
import subprocess
# os_cmd = 'ls -lah'
os_cmd = "arecord --device=hw:1,0 -d 3 --format S16_LE --rate 44100 -c1 test4.wav"
print('os:',os_cmd)
#os.system(os_cmd)
# arecord --device=hw:1,0 -d 3 --format S16_LE --rate 44100 -c1 test2.wav
#command = ["arecord","--device=hw:1,0", "-d 3", "--format S16_LE", "--rate 44100", "-c1 test3.wav"]
command = ["arecord","--device=hw:1,0", "-d","3", "--format","S16_LE", "--rate","44100", "-c1","test7.wav"]
#command = ['echo','Hello World']
print(command)


outp = subprocess.check_output(command, stdin=None, stderr=None,shell=False,universal_newlines=False)
print(outp)

'''
outp = subprocess.check_output(command, stdout=None, stderr=None,shell=False)

stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
stdout,stderr = proc_out.communicate()
print('stdout:')
print(stdout)
print('stderr:')
print(stderr)
'''

