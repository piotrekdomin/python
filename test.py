#!/usr/bin/python3

from pca9685_new import *
import sys

pca_init()
while True:
    _option = input("Input an option: s - single channel(d - by %), a - aquarium(z - by %), q - quit, w - cut-off all, p - set prescaler, l - set latency in loops or c - check duty(v - by%): ")
    if(_option == 'q'):
        sys.exit(0)
    if(_option == 'w'):
        emerg_all_off()
        continue
    if(_option == 'c'):
        check_duty_all()
        continue
    if(_option == 'v'):
        check_duty_all_percent()
        continue
    if(_option == 'p'):
        value = input("Input value within 3-200: ")
        set_prescaler(value)
        continue
    if(_option == 'a'):
        dev_aq_pwm_change()
        #dev_percent_aq_pwm_change()
        continue
    if(_option == 'z'):
        #dev_aq_pwm_change()
        dev_percent_aq_pwm_change()
        continue
    if(_option == 'l'):
        dev_set_latency()
    if(_option == 's'):
        _channel = int(input("Input channel[0-15]: "))
        if _channel in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
            #channel = int(_channel)
            dev_pwm_change(_channel)
            #dev_percent_pwm_change(channel)
        else:
            print("Invalid channel!")
            continue
        continue
    if(_option == 'd'):
        _channel = int(input("Input channel[0-15]: "))
        if _channel in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
            #channel = int(_channel)
            #dev_pwm_change(channel)
            dev_percent_pwm_change(_channel)
        else:
            print("Invalid channel!")
            continue
        continue
    else:
        print("Option " + str(_option) + " not supported.")
        continue