
#! /bin/sh

# WPSボタンを押す
sleep 5
/sbin/wpa_cli -i wlan0 wps_pbc
sleep 5

# 5秒周期でWifi接続が確立したかチェックする
#while sleep 5;do
#	STATUS=`/sbin/wpa_cli -i wlan0 status | grep ip_address= | cut -d = -f 2`
#	case $STATUS in
#                # 接続失敗
#		INACTIVE)
#                        # もう一度WPSボタンを押す
#			/sbin/wpa_cli -i wlan0 wps_pbc
#			;;
#                # 接続成功
#		COMPLETED)
#			exit 0
#			;;
#	esac
#done