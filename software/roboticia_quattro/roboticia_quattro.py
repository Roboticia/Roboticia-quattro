import os
import sys
import numpy
import ctypes

from functools import partial

from poppy.creatures import AbstractPoppyCreature

from .primitives.leg import Leg

from .robot_sensors import ArduinoSensor


class RoboticiaQuattro(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        #robot.attach_primitive(Leg(robot,['m41','m42','m43']), 'leg_AD')
        #robot.attach_primitive(Wave(robot), 'wave')
    
        if robot.simulated :
            cls.vrep_hack(robot)
            cls.add_vrep_methods(robot)
        else :
            robot.arduino = Arduino('arduino_uno','COM4',115200)
            robot.sensors.append('arduino')
    
    
    
    
     

    @classmethod
    def vrep_hack(cls, robot):
        # fix vrep orientation bug
        wrong_motor = []
        
        for m in wrong_motor:
            m.direct = not m.direct
            m.offset = -m.offset
            
    @classmethod
    def add_vrep_methods(cls, robot):
        from pypot.vrep.controller import VrepController
        from pypot.vrep.io import remote_api

        def set_vrep_force(robot, vector_force, shape_name):
            """ Set a force to apply on the robot. """
            vrep_io = next(c for c in robot._controllers
                           if isinstance(c, VrepController)).io

            raw_bytes = (ctypes.c_ubyte * len(shape_name)).from_buffer_copy(shape_name)
            vrep_io.call_remote_api('simxSetStringSignal', 'shape',
                                    raw_bytes, sending=True)

            packedData = remote_api.simxPackFloats(vector_force)
            raw_bytes = (ctypes.c_ubyte * len(packedData)).from_buffer_copy(packedData)
            vrep_io.call_remote_api('simxSetStringSignal', 'force',
                                    raw_bytes, sending=True)

        robot.set_vrep_force = partial(set_vrep_force, robot)