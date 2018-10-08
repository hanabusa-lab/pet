#!/bin/bash
ps aux | grep python | awk '{print "kill -9", $2}' | sh
#ps aux | grep www | awk '{print "kill -9", $2}' | sh
#ps aux | grep npm | awk '{print "kill -9", $2}' | sh

