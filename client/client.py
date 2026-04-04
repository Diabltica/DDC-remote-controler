import sys
import serial
from monitorcontrol import get_monitors
from monitorcontrol import vcp

def connectSerial(port, baudrate, timeout):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connected to {port} at {baudrate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
        return None

def processCommand(monitor, command, state):
    inputPerso=["DVI1","HDMI1","HDMI1"]
    inputPro=["HDMI1","HDMI1","ANALOG1"]
    
    if state[command] == 0:
        switchInput(monitor[command], inputPro[command])
        state[command] = 1

    elif state[command] == 1:
        switchInput(monitor[command], inputPerso[command])
        state[command] = 0
    
    return state

def switchInput(monitor, newInput):
    try:
        with monitor:
            monitor.set_input_source(newInput)
    except vcp.VCPError:
        print("error")

if "__main__" == __name__:
    PORT = 'COM15'  # Change to your COM port
    BAUDRATE = 115200
    TIMEOUT = 1
    state = [0,0,0] # 0 perso / 1 pro 
    ser = connectSerial(PORT, BAUDRATE, TIMEOUT)
    if ser == None:
        sys.exit(1)
    monitor = get_monitors()
    while(1):
        line = ser.readline().decode("utf-8");
        if line != "\n" and line != "":
            print(line)
            state = processCommand(monitor, int(line), state)
    

# to get monitor model to differentiate them
# from monitorcontrol import get_monitors

# for monitor in get_monitors():
#     with monitor:
#         print(monitor.get_vcp_capabilities())