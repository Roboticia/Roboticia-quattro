import math as mt
from pypot.primitive import LoopPrimitive

class Leg(LoopPrimitive):
    def __init__(self,robot,leg,refresh_freq=50):
        LoopPrimitive.__init__(self, robot,refresh_freq)
        # you should never access directly to the motors in a primitive, because this is the goal of the Primitives manager 
        # to manage this acces for all the primitives : https://poppy-project.github.io/pypot/primitive.html
        fake_motors = getattr(self.robot, leg)
        self.knee = fake_motors[2]
        self.hip = fake_motors[1]
        self.hip_lateral = fake_motors[0]
        self.motors = fake_motors
        
        # size of segment's leg            
        self.shin = 63
        self.thigh = 55
        self.pelvis = 38
        
    def __repr__(self):
        return ('<Primitive name={self.name}>').format(self=self)
        
        
        
    @classmethod
    def AK_side(cls, side_a,side_b,side_c):
        """
        Take the 3 side of a triangle and return the angles
        """
        try : 
            alpha = mt.acos((side_b**2 + side_c**2 - side_a**2)/(2*side_b*side_c))
            beta = mt.acos((side_a**2 + side_c**2 - side_b**2)/(2*side_a*side_c))
            gamma = mt.pi - alpha - beta
        except ValueError : 
            return (False,0,0,0)
        else :
            return (True,alpha,beta,gamma)

    @classmethod
    def AK_angle(cls, side_a,side_b,gamma):
        """
        Take 2 sides and 1 angle of a triangle and return the missing angles and sides
        """
        side_c = mt.sqrt (side_a**2 + side_b**2 - 2*side_a*side_b*mt.cos(gamma))
        alpha = mt.acos((side_b**2 + side_c**2 - side_a**2)/(2*side_b*side_c))
        beta= mt.pi - alpha - gamma
        return (side_c,alpha,beta)
    
    @property      
    def get_pos(self):
        (side_c,alpha,beta) = Leg.AK_angle(self.thigh,self.shin,mt.pi-abs(mt.radians(self.knee.present_position)))
        # what knee flexion
        flex = mt.copysign(1,self.knee.present_position)
        # calcul de l'angle beta_2 entre side_c et la veticale
        beta_2 = mt.radians(self.hip.present_position)+beta*flex
        theta = mt.radians(self.hip_lateral.present_position)
        
        high_leg = mt.cos(beta_2)*side_c+self.pelvis
        
        high = mt.cos(theta)*high_leg
        distance = mt.sin(beta_2)*side_c
        balance = mt.sin(theta)*high_leg
        
        return (high,distance,flex,balance)
      
    
    def set_pos(self,h,d,b):
        high_leg = mt.sqrt(h**2+b**2)
        side_c = mt.sqrt((high_leg-self.pelvis)**2+d**2)
        beta_2 = mt.asin(d/side_c)
        (status,alpha,beta,gamma) = Leg.AK_side(self.thigh,self.shin,side_c)
        
        angle_hip = mt.degrees(beta_2 - beta*self.f)
        angle_knee = self.f*mt.degrees(mt.pi - gamma)
        angle_hip_lateral = mt.degrees(mt.asin(b/high_leg))
            
        return(status,angle_hip_lateral, angle_hip, angle_knee)
        
    def h_limit(self,d):
        pass
        
    def d_limit(self,h):
        pass
        
    def setup(self):
        (self.h,self.d,self.f,self.b) = self.get_pos
        
        
    def update(self):
        (status,angle_hip_lateral, angle_hip, angle_knee) = self.set_pos(self.h,self.d,self.b)
        if status :
            self.hip.goal_position = angle_hip
            self.knee.goal_position = angle_knee
            self.hip_lateral.goal_position = angle_hip_lateral
        else :
            print('invalid range')
            self.setup()
        
    
    def move(self,speed,cycle,*args):
        if cycle == 'go':
            if len(args)>0 and self.d+speed > args[0] : #multiplier par le signe de la vitesse pour gérer les vitesses négatives
                self.d = args[0]
                return True
            else :
                self.d += speed
                return False
            
                     
        if cycle == 'back':
            if self.h-speed > args[0] and self.d-speed > args[1] :
                self.d -= speed
                self.h -= speed
                return False
            
            if self.d-speed > args[1] :
                self.h = args[0]
                self.d -= speed
                return False
            
            if self.h+speed < args[2] : 
                self.d = args[1]
                self.h += speed
                return False
            else :
                self.h = args[2]
                return True
            
                    
        if cycle == 'balance':
            if len(args)>0 and mt.copysign(1,speed)*(self.b+speed) > mt.copysign(1,speed)*args[0] : #multiplier par le signe de la vitesse pour gérer les vitesses négatives
                self.b = args[0]
                return True
            else :
                self.b += speed
                return False
            
        if cycle=='release':
            if self.h-speed < limit : #multiplier par le signe de la vitesse pour gérer les vitesses négatives
                self.h = limit
                return True
            else :
                self.h -= speed
                return False
            
        