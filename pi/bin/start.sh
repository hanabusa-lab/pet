#!/bin/bash

#dont execute if img_mgr is running 
psnum=`ps aux | grep pet_mgr | wc -l`

#echo $psnum
if [ $psnum -gt 1 ]; then
	echo "process is running. process num=[$psnum]. stop"
	exit
else 
	echo "process is not running. process num=[$psnum]. exec process"
fi

cd /pet/bin

#exec pet_mgr.py
python3 pet_mgr.py& 
#exec led_mgr.py
sudo python3 led_mgr.py& 

#exec web node
#cd /mukudori/web
#DEBUG=web:* npm start&

