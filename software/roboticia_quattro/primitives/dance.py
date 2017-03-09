import math as mt
from pypot.primitive import Primitive

class Leg(Primitive):
    def __init__(self,robot,motors_name):
        self.robot = robot
        Primitive.__init__(self, robot)
        self.fake_motors=[]
        for name in motors_name:
            self.fake_motors.append(getattr(self.robot, name))  
            
        self.shin = 79
        self.thigh = 72
        
    @classmethod
    def AK_angle(cls,side_a,side_b,gamma):
        side_c = mt.sqrt (side_a**2 + side_b**2 - 2*side_a*side_b*mt.cos(gamma))
        alpha = mt.acos((side_b**2 + side_c**2 - side_a**2)/(2*side_b*side_c))
        beta= mt.pi - alpha - gamma
        return (side_c,alpha,beta)
        
    @property      
    def get_pos(self):
        (side_c,alpha,beta) = Leg.AK_angle(self.thigh,self.shin,mt.pi-abs(mt.radians(self.fake_motors[2].present_position)))
        # calcul de l'angle beta_2 entre side_c et la veticale
        beta_2 = mt.radians(self.fake_motors[1].present_position)+mt.copysign(beta,self.fake_motors[2].present_position)
        h = mt.cos(beta_2)*side_c
        d = mt.sin(beta_2)*side_c
        return (h,d)
        
        
        
    def setup(self):
        pass
        '''
        for m in self.fake_motors.keys():
            self.position[m] = []
        self.python_time=[]
        self.pypot_time=[]
        '''
    def run(self):
        pass
        '''
        t0 = time.time()
        while not self.should_stop():
            for m in self.fake_motors.keys():
                self.position[m].append(self.fake_motors[m].present_position)
                self.load[m].append(self.fake_motors[m].present_load)
                self.speed[m].append(self.fake_motors[m].present_speed)
            self.python_time.append(time.time()-t0)
            self.pypot_time.append(self.elapsed_time)
            time.sleep(0.02)
            '''