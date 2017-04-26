import os
import sys
import numpy
import ctypes

from functools import partial

from pypot.creatures import AbstractPoppyCreature

from pypot.robot.controller import SensorsController
from pypot.robot.sensor import Sensor
from pypot.sensor import ArduinoSensor

from .primitives.leg import Leg
from .primitives.start_posture import StartPosture

class ForceSensor(Sensor):
    """
    Define a phidget force sensor
    """
    def __init__(self, name, arduino):
        Sensor.__init__(self, name)
        self._arduino = arduino
        
    def __repr__(self):
        return ('<ForceSensor name={self.name} '
                'force = {self.force}>').format(self=self)
    
    def close(self):
        self._arduino.close()
        
    @property
    def force(self):
        return self._arduino.sensor_dict[self.name]
        
class VrepForceSensor(Sensor):
    """
    Define a vrep force sensor
    """
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.force = 0.0
        
    def __repr__(self):
        return ('<ForceSensor name={self.name} '
                'force = {self.force}>').format(self=self)

class VrepForceController(SensorsController):
    """
    Update the value of the force sensor read in Vrep
    """
    def setup(self):
        """ Forces a first update to trigger V-REP streaming. """
        self.update()

    def update(self):
        """ Update the value of the force sensor. """

        for s in self.sensors:
            s.force = self.io.call_remote_api('simxReadForceSensor', self.io.get_object_handle(s.name), streaming=True)[1][2]*100

class RoboticiaQuattro(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        robot.attach_primitive(Leg(robot,'leg1'), 'leg_1')
        robot.attach_primitive(Leg(robot,'leg2'), 'leg_2')
        robot.attach_primitive(Leg(robot,'leg3'), 'leg_3')
        robot.attach_primitive(Leg(robot,'leg4'), 'leg_4')
        
        robot.attach_primitive(StartPosture(robot,3), 'start_posture')
        
    
        if robot.simulated :
            from pypot.vrep.controller import VrepController
            vrep_io = next(c for c in robot._controllers
                           if isinstance(c, VrepController)).io
            sensors = [VrepForceSensor(name) for name in ('f1','f2','f3','f4')]
            vfc = VrepForceController(vrep_io, sensors)
            vfc.start()
            robot._sensors.extend(vfc.sensors)
            for s in vfc.sensors :
                setattr(robot, s.name, s)
            cls.vrep_hack(robot)
            cls.add_vrep_methods(robot)
        else :
            arduino = ArduinoSensor('arduino','/dev/ttyUSB0',115200)
            arduino.start()
            sensors = [ForceSensor(name, arduino) for name in ('f1','f2','f3','f4')]
            robot._sensors.extend(sensors)
            for s in sensors :
                setattr(robot, s.name, s)
            for m in robot.motors :
                m.pid = (6.0,10.0,0.0)
    
    
    
    
     

    @classmethod
    def vrep_hack(cls, robot):
        # fix vrep orientation bug
        wrong_motor = [robot.m13,robot.m23,robot.m33,robot.m43]
        
        for m in wrong_motor:
            m.direct = not m.direct
            m.offset = -m.offset
            
    @classmethod
    def add_vrep_methods(cls, robot):
        from pypot.vrep.io import remote_api

        def set_vrep_force(robot, vector_force, shape_name):
            """ Set a force to apply on the robot. """
            

            raw_bytes = (ctypes.c_ubyte * len(shape_name)).from_buffer_copy(shape_name)
            vrep_io.call_remote_api('simxSetStringSignal', 'shape',
                                    raw_bytes, sending=True)

            packedData = remote_api.simxPackFloats(vector_force)
            raw_bytes = (ctypes.c_ubyte * len(packedData)).from_buffer_copy(packedData)
            vrep_io.call_remote_api('simxSetStringSignal', 'force',
                                    raw_bytes, sending=True)

        robot.set_vrep_force = partial(set_vrep_force, robot)