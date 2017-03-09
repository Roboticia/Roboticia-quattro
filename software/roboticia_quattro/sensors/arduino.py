from pypot.robot.sensor import Sensor
from pypot.utils import StoppableLoopThread
import serial
import json

class ArduinoSensor(Sensor):
    """ Give acces to arduino sensor
        
    """
    
    def __init__(self, name, port, baud, sync_freq=50.0):
        Sensor.__init__(self, name)
        
        self.port = port
        self.baud = baud
        self._controller = StoppableLoopThread(sync_freq, update=self.update)
        
    def start(self):
        self._ser = serial.Serial(self.port, self.baud)
        self._controller.start()

    def close(self):
        self._controller.stop()
        self._ser.close()

    def update(self):
        self.line = self._ser.readline()
        while self._ser.inWaiting() > 0:
            self.line = self._ser.readline()
        self.sensor_dict = json.loads(self.line)