"""
汎用学習リモコン トイレ洗浄用

Interval_cleaning.py


2022/06/20  トイレ洗浄用
    01      待機状態(modeFile.txtが「mode選択」)であれば、なにもしない
            運用状態(modeFile.txtが「運用 mode」)である場合のみカウントダウンして洗浄を行う。
            カウントダウンのリセットはirrp_data_code04.pyが赤外線コードを受信した際に行う
            なので、人間系が洗浄した時もリセットされる。

            カウントダウンファイルwash_countdown.txtを読み込む(分単位)
            -1分して、上書き保存する。
            1分待機
            カウントダウンが０になっていたら、洗浄コマンドを発行する。
2022/06/23  カウントダウンが異常時にリセットする
2022/06/24  1分周期を微調整


"""
import RPi.GPIO as GPIO
import time
import sys
import datetime
import os
from nobu_LIB import Lib_OLED

import getpass
import timeout_decorator
import shutil

# ユーザー名を取得
user_name = getpass.getuser()
print('user_name',user_name)
path = '/home/' + user_name + '/T_remocon/' # cronで起動する際には絶対パスが必要
# path = '/home/' + 'tk' + '/T_remocon/' # systemdで起動する際にはrootになり絶対パスが必要

disp_size = 32 # or 64
iR_LED = '22'


###################log print#####################
# 自身のプログラム名からログファイル名を作る
import sys
args = sys.argv
logFileName = args[0].strip(".py") + "_log.csv"
print(logFileName)
# ログファイルにプログラム起動時間を記録
import csv
# 日本語文字化けするので、Shift_jisやめてみた。
f = open(logFileName, 'a')
csvWriter = csv.writer(f)
csvWriter.writerow([datetime.datetime.now(),'  program start!!'])
f.close()
#----------------------------------------------
def log_print(msg1="",msg2="",msg3=""):
    # エラーメッセージなどをプリントする際に、ログファイルも作る
    # ３つまでのデータに対応
    print(msg1,msg2,msg3)
    # f = open(logFileName, 'a',encoding="Shift_jis") 
    # 日本語文字化けするので、Shift_jisやめてみた。
    f = open(logFileName, 'a')
    csvWriter = csv.writer(f)
    csvWriter.writerow([datetime.datetime.now(),msg1,msg2,msg3])
    f.close()
################################################

#print message at the begining ---custom function
def print_message():
    log_print ('|********************************|')
    log_print ('| interval_cleaning.py     2     |')
    log_print ('|********************************|')
    log_print(datetime.datetime.now())
    # print('上限温度',temp_uper,'下限温度',temp_lower,'\n')
    print ('Program is running...')
    print ('Please press Ctrl+C to end the program...')


def OLED_disp(OLED_disp_text,timer=0):
    # print('point0',OLED_disp_text)
    Lib_OLED.SSD1306(OLED_disp_text,disp_size)
    # print('point1')
    time.sleep(timer)

@timeout_decorator.timeout(15)
# もし、iR発信し続ける様なことがあると、破損するので、その対策
def iR_send(send_comand):
    try:
        # cronで起動する際には絶対パスが必要
        # send_comand = 'python3 /home/pi/aircontrol/irrp.py -p -g22 -f ' + send_comand
        send_comand = path + send_comand + ' test'
        send_comand = 'python3 ' + path + 'irrp_long.py -p -g' + iR_LED + ' -f ' + send_comand
        # 設定変更のスタート時間を記憶
        log_print(send_comand)
        # 設定変更の赤外線送出
        os.system(send_comand)
        return
    except:
        OLED_disp('iR送信エラー',2)
        destroy_stop()
        log_print('エラー発生')
        return


#main function
def main():
    print_message()
    # OLED_disp('welcom remocon',2)
    print(path)

    while True:

        # 運用状態取得 (modeFile.txt)
        with open(path + 'modeFile.txt') as f:
            運用状態 = f.read()

        if  運用状態 == '運用 mode' :

            # カウントダウンファイルを読み込む
            with open(path + 'wash_countdown.txt') as f:
                カウントダウン = int(f.read())

            log_print(カウントダウン)
            if カウントダウン == 0:
                # 洗浄コードを発行
                OLED_disp('洗浄コードを発行',2)
                iR_send('water-small')

            # カウントダウンを-1する
            カウントダウン = カウントダウン -1
            # カウントダウンファイルを書き込む
            with open(path + 'wash_countdown.txt', mode='w') as f: #上書き
                f.write(str(カウントダウン))

            time.sleep(59.8)

            if カウントダウン < -1:
                # あるはずのないカウントダウンなのでリセットする
                try:
                    log_print('wash countdown reset',カウントダウン)
                    shutil.copyfile(path + "wash_time_minut.txt", path + "wash_countdown.txt")
                except:
                    log_print('wash countdown file not found',カウントダウン)
                pass

        else:
            time.sleep(10)


def destroy_stop():
    #release resource
    GPIO.cleanup()

# if run this script directly ,do:
if __name__ == '__main__':

        main()
