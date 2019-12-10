import time
from time import gmtime, strftime
import serial

def write_cmd(p, cmd):
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
    else:
        print("Cmd: {}".format(cmd.replace("\r", "")))
        print("Error.")
        
portName = "COM7"
phone = serial.Serial(port = portName,
                      baudrate = 115200,
                      bytesize = serial.EIGHTBITS,
                      parity = serial.PARITY_NONE,
                      stopbits = serial.STOPBITS_ONE,
                      timeout = 5) # Unit in second
                      
# Initialize the SIM7020e
write_cmd(phone, 'AT')

write_cmd(phone, 'AT+CPIN?')
write_cmd(phone, 'AT*MCGDEFCONT="IP","internet.iot"')
write_cmd(phone, 'AT+CFUN=1')

write_cmd(phone, 'AT+CBAND=8')
write_cmd(phone, 'AT+CGREG=1')
write_cmd(phone, 'AT+CSQ')
write_cmd(phone, 'AT+COPS?')
write_cmd(phone, 'AT+CGATT?')
write_cmd(phone, 'AT+CGREG?')

# http GET method
url = "http://ec2-54-175-179-28.compute-1.amazonaws.com"

DBName = "INCM01"
now = strftime("%Y%m%d%H%M%S")
idNum = "5999"
data= "/update_general.php?site={}&time={}&id={}&roll=0&pitch=0&yaw=0&field1=0&field2=0&field3=0".format(DBName, now, idNum)

write_cmd(phone, 'AT+CHTTPDISCON=0')
write_cmd(phone, 'AT+CHTTPCREATE=' + url)
write_cmd(phone, 'AT+CHTTPCREATE?')
write_cmd(phone, 'AT+CHTTPCON=0')
write_cmd(phone, 'AT+CHTTPSEND=0,0,' + data)
write_cmd(phone, 'AT+CHTTPDISCON=0')
write_cmd(phone, 'AT+CHTTPDESTROY=0')

phone.close
