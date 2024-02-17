def connect():
    import network
    ssid = "PHU LINH"
    password =  "0979292044"
       
    station = network.WLAN(network.STA_IF)
 
    if station.isconnected() == True:
        print("Already connected")
        return
 
    station.active(True)
    station.connect(ssid, password)
 
    if station.isconnected() == False:
        pass

    print("Connection successful")
    print(station.ifconfig())
