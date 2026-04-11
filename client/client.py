import sys
import serial
import serial.tools.list_ports
from monitorcontrol import get_monitors, InputSource
from monitorcontrol import vcp

import gui

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

def getMonitorData(monitors):
    screenData = []

    for m in monitors: 
        with m:
            # print(m.get_vcp_capabilities())
            vcpCap = m.get_vcp_capabilities()
            monInput = []
            for i in vcpCap["inputs"]:
                monInput.append(InputSource(i).name)
            screenData.append([vcpCap["model"],monInput])
    return screenData

def getAvailableCom():
    availableCom = []

    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
            availableCom.append(port)
    
    return availableCom

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
    monitorData = getMonitorData(monitors)

    app = gui.ConfigGUI()

    app.set_com_options(getAvailableCom())
    app.set_screen_options([str(monitorData[0][0]), str(monitorData[1][0]), str(monitorData[2][0])])

    app.set_input_options_for_screen_id(0, monitorData[0][1])
    app.set_input_options_for_screen_id(1, monitorData[1][1])
    app.set_input_options_for_screen_id(2, monitorData[2][1])

    app.set_default_colors("#00ff00", "#ff0000")

    app.mainloop()
    while(1):
        state = syncState(state, monitors)
        sendStateToControler(state, ser)
        line = ser.readline().decode("utf-8");
        if line != "\n" and line != "":
            # print(line)
            processCommand(monitors, int(line), state)
        