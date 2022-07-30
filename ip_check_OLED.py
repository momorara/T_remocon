"""
ip_check.py

2022/01/04 start
2022/01/07  ipgetにてipアドレスを取得
            ipアドレス取得できない場合はwpsを試す
            
pip3 install ipget

wps_set.pyを使って、ipが分かっているか否かを確認する。
ipが分かっていれば、ipを表示して終了。

ip分かっていなければ、
wpsモードに入り5回トライする。

LEDが点灯している間にルーターのwpsボタンを押す。
ip取得に成功すれば、ipを表示して終了。
"""
import RPi.GPIO as GPIO
import subprocess
import sys
import os
import time
import getpass
from nobu_LIB import Lib_OLED
LED = 5
LED1 = 12
GPIO.setwarnings(False)
#set the gpio modes to BCM numberiset
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(LED1,GPIO.OUT,initial=GPIO.LOW)

disp_size = 32 # or 64
def OLED_disp(OLED_disp_text,timer=0):
    # print('point0',OLED_disp_text)
    Lib_OLED.SSD1306(OLED_disp_text,disp_size)
    # print('point1')
    time.sleep(timer)

print('ip_check')
OLED_disp('ipアドレス確認',1)

# sudo ifconfig wlan0 down
# sudo ifconfig wlan0 up
# os.system('sudo ifconfig wlan0 down')
# time.sleep(3)
os.system('sudo ifconfig wlan0 up')
# time.sleep(20)

# ipgetを使って、ipアドレスを取得
import ipget
# ipアドレスをipgetにて取得、5秒5回試してダメならあきらめる。
def ip_check():
    count = 0
    ip_adr = 'not'
    while 'not' in ip_adr:
        try:
            a = ipget.ipget()
            try:
                ip_adr = a.ipaddr("eth0")
            except:
                ip_adr = a.ipaddr("wlan0")
            if 'not' in ip_adr:
                print('00',ip_adr)
            else:
                ip_adr = ip_adr.replace('/24','')
                ip_adr = ip_adr.replace('/28','')
                print('01 ip_adr:',ip_adr)
        except :
            print('02',ip_adr)
        count = count +1
        print('1',count,ip_adr)
        if ('not' in ip_adr) == False:
            break
        if count >1 :
            ip_adr = 'noconnect'
            break
        os.system('sudo ifconfig wlan0 down')
        time.sleep(3)
        os.system('sudo ifconfig wlan0 up')
        time.sleep(5)
    return ip_adr

ip_adr = ip_check()
print('2',ip_adr)
OLED_disp(ip_adr,2)
time.sleep(2)
if  ip_adr != 'noconnect':
    exit(0)

# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/T_remocon/' # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/T_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

OLED_disp('LED点灯でWPSを押す',2)

GPIO.output(LED1,GPIO.HIGH)
GPIO.output(LED,GPIO.HIGH)

# wpsを実行してipアドレスを取得する
#os_cmd = 'python3 ' + path + 'wps_set.py'
os_cmd = 'sh ' + path + 'wps.sh'
os.system(os_cmd)
OLED_disp('wps中です',2)

GPIO.output(LED,GPIO.LOW)
GPIO.output(LED1,GPIO.LOW)
OLED_disp('wps終了',2)

exit(0)

os.system('sudo ifconfig wlan0 down')
time.sleep(3)
os.system('sudo ifconfig wlan0 up')
time.sleep(20)

# ipアドレス取得状態を確認
wlan0_wpa_state = '/sbin/wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2'
STATUS = subprocess.Popen(wlan0_wpa_state, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
out, err = STATUS.communicate()
print('1:',out,':', err)

# out = 'COMPLETED' ならipアドレス取得済み それ以外は無効
if out == 'COMPLETED\n' :
    ip_adr = ip_check()
    print('3',ip_adr)
    OLED_disp(ip_adr,0)
    time.sleep(2)
    exit(0)

OLED_disp('LED点灯でWPSを押す',2)
while out != 'COMPLETED\n':
    os.system('sudo ifconfig wlan0 down')
    time.sleep(3)
    os.system('sudo ifconfig wlan0 up')
    time.sleep(20)

    # ipアドレス取得状態を確認
    wlan0_wpa_state = '/sbin/wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2'
    STATUS = subprocess.Popen(wlan0_wpa_state, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = STATUS.communicate()
    print(out, err)

    if out != 'COMPLETED\n':
        GPIO.output(LED1,GPIO.HIGH)
        GPIO.output(LED,GPIO.HIGH)
        # wpsを実行してipアドレスを取得する
        #os_cmd = 'python3 ' + path + 'wps_set.py'
        os_cmd = 'sh ' + path + 'wps.sh'
        os.system(os_cmd)
        GPIO.output(LED,GPIO.LOW)
        GPIO.output(LED1,GPIO.LOW)
    
    # ipアドレス取得状態を確認
    wlan0_wpa_state = '/sbin/wpa_cli -i wlan0 status | grep wpa_state= | cut -d = -f 2'
    STATUS = subprocess.Popen(wlan0_wpa_state, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = STATUS.communicate()
    print(out, err)

ip_adr = ip_check()
print('3',ip_adr)
OLED_disp(ip_adr,2)
time.sleep(2)
exit(0)

