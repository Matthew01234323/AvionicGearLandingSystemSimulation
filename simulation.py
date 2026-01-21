from enum import Enum, auto
from random import randint
import time

class GearState(Enum):
    UP_LOCKED = auto()
    TRANSITIONING_UP = auto()

    DOWN_LOCKED = auto()
    TRANSITIONING_DOWN = auto()

class HydraulicActuators:
    temperature = 30
    angle = 0
    fault = False
    efficiency = 0.12

    def refreshEfficiency(self, windMPH, altitudeFT):
        self.efficiency = (0.10 - (windMPH * 0.00007)) - (altitudeFT * 0.000005)
        if self.temperature < -20:
            self.efficiency *= 0.8
        
        elif self.temperature > 80:
            self.efficiency *= 0.9
    
    def extending(self, timePeriod):
        print(self.efficiency)
        if self.fault == False:
            temp = timePeriod
            for t in range (0,temp):
                time.sleep(0.01)
                timePeriod -= 1
                self.angle += self.efficiency
                if self.angle >= 90: #stop extending at 90 degrees
                    self.angle = 90
                    break
            return self.angle, timePeriod #returns the extended angle and time
        
        else:
            self.log("Command Rejected")

class LandingGearController:
    def __init__(self):
        self.state = GearState.UP_LOCKED

    def log(self, message):
        print(f"[{self.state.name}] {message}")

    def command_gear_down(self):
        if self.state == GearState.UP_LOCKED:
            self.state = GearState.TRANSITIONING_DOWN
            #HydraulicActuators.extending() ~~Add in functionality to ensure hydraulics fully exteneded
            self.log("Gear Deploying")
            #time.sleep(1)
            HydraulicsAngle, timePeriod = HydraulicActuators.extending(Hydraulics, 1200)
            print (HydraulicsAngle)
            print (timePeriod)
            if HydraulicsAngle == 90:
                self.state = GearState.DOWN_LOCKED
                self.log("Gear Deployed")
            else:
                self.log("Insufficient Gear Deployment angle")
        else:
            self.log("Command Rejected, Invalid State")
        
    def command_gear_up(self):
        if self.state == GearState.DOWN_LOCKED:
            self.state = GearState.TRANSITIONING_UP
            self.log("Gear Retracting")
            time.sleep(1)
            self.state = GearState.UP_LOCKED
            self.log("Gear Moved Up")
        else:
            self.log("Command Rejected, Invalid State")

Hydraulics = HydraulicActuators
Hydraulics.temperature = 30
HydraulicActuators.refreshEfficiency(Hydraulics, 100, 3000)
controller = LandingGearController()
controller.command_gear_down()
controller.command_gear_up()
#angle, time = HydraulicActuators.extending(Hydraulics, 1200)
#print(time)