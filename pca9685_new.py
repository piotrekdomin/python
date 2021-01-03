#!/usr/bin/python3

# led_pwm v 1.0.0
# Created by Piotr Domin, piotr.domin=gmail.com, Dec 2020, You can use it for free :)
# Based on Adafruit_PCA9685 code, https://www.instructables.com/Raspberry-Pi-I2C-Python/ and PCA9685 datasheet.
# Main difference with adafruit_pca9685 library is read current register content feature needed to smooth duty regulation.
# SMBus is a debian packet installed by 'sudo apt install -y python3-smbus'
# TODO:
# 0. Move all validations from example code into fuctions, - done
# 1. Add duty validation, - done
# 2. Add duty percentage option, - done
# 2.5. Add latency to loops, value will be stored in unused SUBADDR3 register - done
# 3. Configuration file,
# ...and what else?


import smbus
import time

# i2c bus configuration, You can find by using 'i2cdetect -y [0-9]' from i2c-tools debian packet.
bus_number = 1

# PCA9685 i2c address
address = 0x40

#registers
reg_mode1 = 0x00
store_reg = 0x04 # unused SUBADDR3 is handy now
prescale = 0xfe
ledx_on_l = 0x06
ledx_on_h = 0x07
ledx_off_l = 0x08
ledx_off_h = 0x09
all_led_on_l = 0xfa
all_led_on_h = 0xfb
all_led_off_l = 0xfc
all_led_off_h = 0xfd

# configuration
perc_div = 40.9

# aquarium channels - I have 3 sections already connected. Phisycally 2 ligthning bars with 5 separated sections.
aqua_ch1 = 1
aqua_ch2 = 2
aqua_ch3 = 3
aqua_ch4 = 4
aqua_ch5 = 5

bus = smbus.SMBus(bus_number)

def pca_init():
    #set_prescaler(3)
    set_latency(0)

def write_byte(reg, value):
    value = int(value)
    if(0 <= value <= 255):
        bus.write_byte_data(address, reg, value)
    else:
        print("Wrong value in 'write_byte'!")

def read_byte(reg):
    value = bus.read_byte_data(address, reg)
    return value

def set_prescaler(value):
    value = int(value)
    if(3 <= value <= 200):
        mode1 = read_byte(reg_mode1)
        mode1 = mode1 | (1 << 4) #set sleep mode
        write_byte(reg_mode1, mode1)
        time.sleep(0.005) #wait 5ms
        write_byte(prescale, value)
        mode1 = mode1 % (1 << 4) #reset sleep mode
        write_byte(reg_mode1, mode1)
        check_reg = read_byte(prescale)
        if(check_reg == value):
            print("Prescaler setting confirmed.")
        else:
            print("Prescaler setting goes wrong!")
    else:
        print("Value for 'prescaler' in 'set_prescaler' out of range!")

def dev_set_latency(): # 0-127 - lsb in reg is read only
    curr_val = (read_byte(store_reg) >> 1)
    print("Current latency value: " + str(curr_val))
    new_val = int(input("Input new latency value [0-127]: "))
    if(0 <= new_val <= 127):
        new_val = (new_val << 1)
        write_byte(store_reg, new_val)
    else:
        print("Invalid value in 'dev_set_latency'!")

def set_latency(value): # 0-127 - lsb in reg is read only
    if(0 <= value <= 127):
        value = (value << 1)
        write_byte(store_reg, value)
    else:
        print("Invalid value in 'set_latency'!")

def get_latency():
    latency = read_byte(store_reg)
    return latency

def set_pwm(channel, duty):
    write_byte(ledx_on_l+4*channel, 0x00)
    write_byte(ledx_on_h+4*channel, 0x00)
    write_byte(ledx_off_l+4*channel, duty & 0xff)
    write_byte(ledx_off_h+4*channel, duty >> 8)

def emerg_all_off():
    write_byte(all_led_on_l, 0x00)
    write_byte(all_led_on_h, 0x00)
    write_byte(all_led_off_l, 0x00)
    write_byte(all_led_off_h, 0x00)

def read_pwm(channel):
    byte_h = read_byte(ledx_off_h+4*channel)
    byte_l = read_byte(ledx_off_l+4*channel)
    duty = ( byte_h << 8 ) | byte_l
    return duty

def raise_pwm(old_val, new_val, channel):
    channel = int(channel)
    latency = read_byte(store_reg)
    if(0 <= channel <= 15): # it's redundant, but necesary for lib-like usage
        if(0 <= new_val <= 4095):
            for n in range(old_val,new_val+1,1):
                time.sleep(latency*0.001)
                set_pwm(channel, n)
        else:
            print("Value 'duty' in 'raise_pwm' out of range!")
    else:
        print("Value 'channel' in 'raise_pwm' out of range!")

def fall_pwm(old_val, new_val, channel):
    channel = int(channel)
    latency = read_byte(store_reg)
    if(0 <= channel <= 15):
        if(0 <= new_val <= 4095):
            for n in range(old_val,new_val-1,-1):
                time.sleep(latency*0.001)
                set_pwm(channel, n)
        else:
            print("Value 'duty' in 'fall_pwm' out of range!")
    else:
        print("Value 'channel' in 'fall_pwm' out of range!")

def raise_aq_pwm(old_val, new_val):
    latency = read_byte(store_reg)
    if(0 <= new_val <= 4095):
        for n in range(old_val,new_val+1,1):
            time.sleep(latency*0.001)
            for x in range(aqua_ch1,aqua_ch5+1,1):
                set_pwm(x, n)
    else:
        print("Value 'duty' " + str(new_val) + " in 'raise_aq_pwm' out of range!")

def fall_aq_pwm(old_val, new_val):
    latency = read_byte(store_reg)
    if(0 <= new_val <= 4095):
        for n in range(old_val,new_val-1,-1):
            time.sleep(latency*0.001)
            for x in range(aqua_ch1,aqua_ch5+1,1):
                set_pwm(x, n)
    else:
        print("Value 'duty' in 'fall_aq_pwm' out of range!")


##### these functions are really experimental

def dev_aq_pwm_change():
    prev_value = read_pwm(aqua_ch1)
    print("Actual value: " + str(prev_value))
    value = int(input("Input new value within[0-4095]: "))
    if value > prev_value:
        raise_aq_pwm(prev_value, value)
    elif value < prev_value:
        fall_aq_pwm(prev_value, value)

def dev_pwm_change(channel):
    channel = int(channel)
    prev_value = read_pwm(channel)
    print("Previous value: " + str(prev_value))
    value = int(input("Input new value within[0-4095]: "))
    if value > prev_value:
        raise_pwm(prev_value, value, channel)
    elif value < prev_value:
        fall_pwm(prev_value, value, channel)

def dev_percent_aq_pwm_change():
    prev_value = read_pwm(aqua_ch1)
    p_prev_value = round(prev_value / perc_div) # pca accepts 12bit values, so 1% = 40 and 100% = 4000
    print("Actual value: " + str(p_prev_value) + "%")
    value = int(input("Input new value within[0-100]: "))
    if value > p_prev_value:
        value = round(value * perc_div)
        raise_aq_pwm(prev_value, value)
    elif value < p_prev_value:
        value = round(value * perc_div)
        fall_aq_pwm(prev_value, value)

def dev_percent_pwm_change(channel):
    channel = int(channel)
    prev_value = read_pwm(channel)
    p_prev_value = round(prev_value / perc_div) # pca accepts 12bit values, so 1% = 40 and 100% = 4000
    print("Actual value: " + str(p_prev_value) + "%")
    value = int(input("Input new value within[0-100]: "))
    if value > p_prev_value:
        value = round(value * perc_div)
        raise_pwm(prev_value, value, channel)
    elif value < p_prev_value:
        value = round(value * perc_div)
        fall_pwm(prev_value, value, channel)



##### these functions will be used in prod mode

def aq_pwm_change(value):
    prev_value = read_pwm(aqua_ch1)
    if value > prev_value:
        raise_aq_pwm(prev_value, value)
    elif value < prev_value:
        fall_aq_pwm(prev_value, value)

def pwm_change(channel, value):
    channel = int(channel)
    prev_value = read_pwm(channel)
    if value > prev_value:
        raise_pwm(prev_value, value, channel)
    elif value < prev_value:
        fall_pwm(prev_value, value, channel)

def percent_aq_pwm_change(value):
    prev_value = read_pwm(aqua_ch1)
    p_prev_value = round(prev_value / perc_div) # pca accepts 12bit values, so 1% = 40 and 100% = 4000
    if value > p_prev_value:
        value = round(value * perc_div)
        raise_aq_pwm(prev_value, value)
    elif value < p_prev_value:
        value = round(value * perc_div)
        fall_aq_pwm(prev_value, value)

def percent_pwm_change(channel, value):
    channel = int(channel)
    prev_value = read_pwm(channel)
    p_prev_value = round(prev_value / perc_div) # pca accepts 12bit values, so 1% = 40 and 100% = 4000
    if value > p_prev_value:
        value = round(value * perc_div)
        raise_pwm(prev_value, value, channel)
    elif value < p_prev_value:
        value = round(value * perc_div)
        fall_pwm(prev_value, value, channel)


##### these functions will be used for simple duty change, dev and prod usable

def q_aq_pwm_change(value):
    value = int(value)
    if(0 <= value <= 4095):
       for x in range(aqua_ch1,aqua_ch5+1,1):
           set_pwm(x ,value)
    else:
        print("Wrong value in 'q_aq_pwm_change'!")

def q_pwm_change(channel, value):
    value = int(value)
    if(0 <= value <= 4095):
        if(0 <= channel <= 15):
           set_pwm(channel ,value)
        else:
            print("Wrong channel in 'q_pwm_change'!")
    else:
        print("Wrong value in 'q_pwm_change'!")

def q_percent_aq_pwm_change(value):
    value = int(value)
    if(0 <= value <= 100):
        value = round(value * perc_div)
        for x in range(aqua_ch1,aqua_ch5+1,1):
            set_pwm(x ,value)
    else:
        print("Wrong value in 'q_percent_aq_pwm_change'!")

def q_percent_pwm_change(channel, value):
    value = int(value)
    if(0 <= value <= 4095):
        value = round(value * perc_div)
        if(0 <= channel <= 15):
           set_pwm(channel ,value)
        else:
            print("Wrong channel in 'q_percent_pwm_change'!")
    else:
        print("Wrong value in 'q_percent_pwm_change'!")

def check_duty_all():
    for i in range(0,16,1):
        duty = read_pwm(i)
        print("Duty for channel: [" + str(i) + "]: " + str(duty))

def check_duty_all_percent():
    for i in range(0,16,1):
        duty = round(read_pwm(i) / perc_div)
        print("Duty for channel: [" + str(i) + "]: " + str(duty) + "%")
