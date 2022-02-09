##########Library##########
import machine
import network
import ConnectWifi
import urequests
from umqtt.simple import MQTTClient
import dht
import time
import json
from bmp180 import BMP180
from machine import I2C, Pin, ADC, PWM
import sys

##########Connect Wifi##########
ssid = "PHU LINH"
password =  "0979292044"
       
station = network.WLAN(network.STA_IF)
     
if station.isconnected() == True:
    print("Already connected")
else: 
    station.active(True)
    station.connect(ssid, password)
 
    if station.isconnected() == False:
        print('Connection failed')
    else:    
        print("Connection successful")
        print(station.ifconfig())
#ConnectWifi.connect()

##########Thingsboard variables and constants##########
username="aArsXRF8kEu0Ov4DmvNy"
broker=  "thingsboard.cloud"
topic = "v1/devices/me/telemetry"
topic_sub = "v1/devices/me/rpc/request/+" 
Mqtt_CLIENT_ID = "22"     
PASSWORD=""
client = MQTTClient(client_id=Mqtt_CLIENT_ID, server=broker, port=1883, user=username, password=PASSWORD, keepalive=10000)
UPDATE_TIME_INTERVAL = 1000 
last_update = time.ticks_ms()
data = dict()
data1 = dict()
message = ""

##########BMP180##########
bus =  I2C(scl=Pin(22), sda=Pin(21), freq=100000) 
bmp180 = BMP180(bus)
bmp180.oversample_sett = 2
bmp180.baseline = 101325

##########LED sensor##########
LDR = ADC(Pin(36))

##########LED##########
led = Pin(23, Pin.OUT)

##########Buzzer##########
p18 = Pin(18, Pin.OUT)
buzzer = PWM(p18)
buzzer.freq(1047)
buzzer.duty(0)

##########Call back function##########
def call_back_function(topic, msg): 
     global message 
     message = msg.decode().strip("'\n") 
     print((topic, msg)) 
client.set_callback(call_back_function)

client.connect()
print('1')
##########Location##########
response = urequests.get('http://ip-api.com/json/')
parsed = response.json()
data1["Latitude"] = parsed["lat"]
data1["Longitude"] = parsed["lon"]
data3 = json.dumps(data1)
client.publish("v1/devices/me/attributes",data3)

##########Main loop##########
while True:
    while station.isconnected() == True:
        try:
            if time.ticks_ms() - last_update >= UPDATE_TIME_INTERVAL:
                t = bmp180.temperature
                p = bmp180.pressure
                a = bmp180.altitude
                s = LDR.read()
    
                data["Temperature"] = t
                data["Pressure"] = p
                data["Altitude"] = a
                data["Light"] = s / 4000 * 100
            
                data2=json.dumps(data)
                #client.connect()
        
                #client.publish(topic, telemetry)
                client.publish(topic,data2)
                client.subscribe(topic_sub)
                client.check_msg()
                if message != "":
                    parsed = json.loads(message)
                    print(message)
                    if parsed["params"] == True:
                        led.on()
                        buzzer.duty(15)
                    else:
                        led.off()
                        buzzer.duty(0)
                #client.disconnect()

                print("Sent")
                last_update = time.ticks_ms()
        except KeyboardInterrupt: 
            print('Ctrl-C pressed...exiting') 
            client.disconnect()
            buzzer.deinit()
            sys.exit()
    else:
        station.connect(ssid, password)
    