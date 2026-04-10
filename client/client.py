import sys
import serial
from monitorcontrol import get_monitors, InputSource
from monitorcontrol import vcp

def connectSerial(port, baudrate, timeout):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connected to {port} at {baudrate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
        return None

def processCommand(monitors, command, state):
    global inputPerso, inputPro
    
    if state[command] == 0:
        setMonitorInput(monitors[command], inputPro[command])
        state[command] = 1

    elif state[command] == 1:
        setMonitorInput(monitors[command], inputPerso[command])
        state[command] = 0
    return state

def setMonitorInput(monitors, newInput):
    try:
        with monitors:
            monitors.set_input_source(newInput)
    except vcp.VCPError:
        print("error")

def getMonitorInputSource(monitors):
    sources = []
    try:
        for m in monitors:
            with m:
                sources.append(InputSource(m.get_input_source()).name)
        return sources
    except vcp.VCPError:
        print("error")

def syncState(state, monitors):
    global inputPerso
    actualSource = None
    while actualSource == None:
        actualSource = getMonitorInputSource(monitors)

    for i in range(len(actualSource)):
            state[i] = ((inputPerso[i] == actualSource[i])+1)%2
            # print("input perso: "+ inputPerso[i])
            # print("actual input: "+ actualSource[i])
            # print("state: "+ str(state[i]))
    return state

def sendStateToControler(state, ser):
    ser.write(bytes((str(state[0])+str(state[1])+str(state[2])).encode()))

if "__main__" == __name__:
    PORT = 'COM15'  # Change to your COM port
    BAUDRATE = 115200
    TIMEOUT = 1
    inputPerso=["DVI1","HDMI1","HDMI1"]
    inputPro=["HDMI1","HDMI1","ANALOG1"]
    state = [0,0,0] # 0 perso / 1 pro 
    ser = connectSerial(PORT, BAUDRATE, TIMEOUT)
    if ser == None:
        sys.exit(1)
    monitors = get_monitors()
    while(1):
        state = syncState(state, monitors)
        sendStateToControler(state, ser)
        line = ser.readline().decode("utf-8");
        if line != "\n" and line != "":
            # print(line)
            processCommand(monitors, int(line), state)
        