import time
import RPi.GPIO as GPIO
import serial

result = []
power_key = 4

#portName = "COM7"
#portName = "/dev/ttyS0"  # 3B+
portName = "/dev/serial0" # pi zero

phone = serial.Serial(port = portName,
                      baudrate = 115200,
                      bytesize = serial.EIGHTBITS,
                      parity = serial.PARITY_NONE,
                      stopbits = serial.STOPBITS_ONE,
                      timeout = 5) # Unit in second
phone.flushInput()

def write_cmd(p, cmd):
    global result
    cmd = cmd + str("\r\n")
    p.write(cmd.encode("utf-8"))    
    time.sleep(0.5)
    if phone.inWaiting():
        result = phone.read(phone.inWaiting())    
    result = result.decode("utf-8").splitlines()
    result = list(filter(lambda a: a != '', result))
    
    if 'OK' in result:
        print("Cmd: {}".format(cmd.replace("\r", "")))        
        print("Response: {}".format(result[1]))
        print("--------------")
        result = []
        return True
    else:
        print("Cmd: {}".format(cmd.replace("\r", "")))
        print("Error.")
        print("--------------")
        result = []
        return False

def power_on(power_key):
    print('SIM7000e is starting')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key,GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(1)
    phone.flushInput()
    print('SIM7000e is ready')

def power_down(power_key):
	print('SIM7000e is logging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(1)
	print('Good bye')

# Power on the SIM7000e
power_on(power_key)

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

while True:
    try:
        write_cmd(phone, 'AT+CGNSINF')    
        result = result[1]
        result = result.split()
        result = result.pop()
        result = result.split(',') 
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
                continue

            with open(queryFid, "a") as file:            
                for item in NMEAinf:
                    file.write("%s," % item)
                file.write("\n")
                print("NMEAinf: {}".format(NMEAinf))
                ii += 1            
        else:
            print("Wait for the GNSS ready.")
            time.sleep(0.5)
    except:
        pass


        
                      