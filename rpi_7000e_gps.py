import time
from time import gmtime, strftime
import serial
result = []

def write_cmd(p, cmd):
    global result
    cmd = cmd + str("\r")
    p.write(cmd.encode("utf-8"))
    time.sleep(0.5)
    result = phone.read(1000)
    result = result.decode("utf-8").splitlines()
    result = list(filter(lambda a: a != '', result))
    
    if 'OK' in result:
        print("Cmd: {}".format(cmd.replace("\r", "")))        
        print("Response: {}".format(result[1]))
        print("--------------")
        return True
    else:
        print("Cmd: {}".format(cmd.replace("\r", "")))
        print("Error.")
        print("--------------")
        return False

#portName = "COM7"
portName = "/dev/ttyUSB3"

phone = serial.Serial(port = portName,
                      baudrate = 115200,
                      bytesize = serial.EIGHTBITS,
                      parity = serial.PARITY_NONE,
                      stopbits = serial.STOPBITS_ONE,
                      timeout = 5) # Unit in second

# Initialize the SIM7000e
while True:    
    if write_cmd(phone, 'AT'):
        break
    time.sleep(2) 

# Turn on GNSS power supply
while True:
    if write_cmd(phone, 'AT+CGNSPWR=1'):
        break
    time.sleep(2)

# Read GNSS navigation information
flag = 0
ii = 0
while (ii < 200):
    write_cmd(phone, 'AT+CGNSINF')    
    result = result[1]
    result = result.split()
    result = result.pop()
    result = result.split(',') 
    try:
        if (result[1] == '1'): # Fix status = 1
            NMEAinf = [int(float(result[2])),  # timeStamp
                       float(result[3]),       # latitude
                       float(result[4]),       # longitude
                       float(result[5]),       # MSL altitude
                       int(result[14]),        # satellites in view
                       int(result[15])]        # satellites used

            if (flag == 0):
                queryFid = "{}_GNSS_record.txt".format(int(float(result[2])))
                with open(queryFid, "a") as file:
                    file.write("---------------Start record---------------")
                    file.write("\n")
                    for item in NMEAinf:
                        file.write("%s," % item)
                    file.write("\n")
                    flag = 1

            with open(queryFid, "a") as file:            
                for item in NMEAinf:
                    file.write("%s," % item)
                file.write("\n")
                print("NMEAinf: {}".format(NMEAinf))
                ii += 1            
        else:
            print("Wait for the GNSS ready.")
    except:
        pass    
    time.sleep(0.5)                    