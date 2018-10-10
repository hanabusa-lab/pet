#python servoscanLR.py

import time
import os

pathdir=os.path.dirname(os.path.abspath(__file__))
path1="/PiBits/ServoBlaster/user/servod --p1pins=7 --pcm"
pathsudo="sudo "
pathkill="sudo killall servod"

path=pathsudo+pathdir+path1
print(path)

os.system(path)

#servo1=X
servo1range=45
count = 1
num = 0

while num < 2:
  com1="echo "
  servonum1=0
  if count % 4 == 1:
    servo1range = 45
  elif count % 4 == 2:
    servo1range = 60
  elif count % 4 == 3:
    servo1range = 90
  elif count % 4 == 0:
    servo1range = 60
  servoang1=servo1range
  com2="% | sudo tee /dev/servoblaster"
  str2=com1+str(servonum1)+"="+str(servoang1)+com2
  os.system(str2)
  time.sleep(2)
  count = count + 1


#os.system(pathkill)