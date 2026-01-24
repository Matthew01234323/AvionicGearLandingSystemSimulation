from enum import Enum, auto
from random import randint
import time
import logging as logWrite

logWrite.basicConfig(
    filename = "simulationLog",
    filemode = "a",
    level = logWrite.INFO,
    format = "%(asctime)s - %(levelname)s : %(message)s",
    datefmt= "%H:%M:%S"
    )

def hydraulicDebug(self, timePeriod):
    if debug == True:
        print ("time left:", timePeriod)
        print ("efficiency:", self.efficiency)

def timePause (delay):
    if timeControls == True:
        time.sleep(0.01)


class GearState(Enum):
    UP_LOCKED = auto()
    TRANSITIONING_UP = auto()

    DOWN_LOCKED = auto()
    TRANSITIONING_DOWN = auto()

    STATIONARY_LOCKED = auto()
    STATIONARY = auto()

class HydraulicActuators:
    temperature = 30
    angle = 0
    fault = False
    efficiency = 0.12

    def refreshEfficiency(self, windMPH, altitudeFT):       # Calculates the efficiency of the hydraulics
        self.efficiency = (0.10 - (windMPH * 0.00007)) - (altitudeFT * 0.000005)
        if self.temperature < -20:
            self.efficiency *= 0.8
        
        elif self.temperature > 80:
            self.efficiency *= 0.9
    
    def extending(self, timePeriod):
        if self.fault == False:
            temp = timePeriod
            for t in range (0,temp):   
                timePause(0.01)                         # causes a real time simulation delay
                timePeriod -= 1
                self.angle += self.efficiency
                if self.angle >= 90:                        # stops extending at 90 degrees
                    self.angle = 90
                    break
            hydraulicDebug (self, timePeriod)
            return self.angle, timePeriod                   # returns the extended angle and time

    def retracting(self, timePeriod):
        if self.fault == False:
            temp = timePeriod
            for t in range (0,temp):
                timePause (0.01)                            # causes a real time simulation delay
                timePeriod -= 1
                self.angle -= self.efficiency
                if self.angle <= 0:                        # stops extending at 90 degrees
                    self.angle = 0
                    break
            hydraulicDebug (self, timePeriod)
            return self.angle, timePeriod                   # returns the extended angle and time

class LandingGearController:
    def __init__(self):
        self.state = GearState.UP_LOCKED

    def command_gear_down(self):
        if self.state == GearState.UP_LOCKED:                       # Confirms the gear is in a valid state
            self.state = GearState.TRANSITIONING_DOWN
            logWrite.info("Gear Deploying")
            HydraulicsAngle, timePeriod = HydraulicActuators.extending(Hydraulics, 1200) # Calls the hydraulics to move
            if HydraulicsAngle == 90:                               # If the gear does extend enough
                self.state = GearState.DOWN_LOCKED
                logWrite.info("Gear Deployed")
            else:                                                   # If the gear does not extend enough
                logWrite.warning("Insufficient Gear Deployment angle")
        else:
            logWrite.warning("Command Rejected")
        
    def command_gear_up(self):
        if self.state == GearState.DOWN_LOCKED:                     # Confirms the gear is in a valid state
            self.state = GearState.TRANSITIONING_UP
            logWrite.info("Gear Retracting")
            HydraulicsAngle, timePeriod = HydraulicActuators.retracting(Hydraulics, 1200) # Calls the hydraulics to move
            if HydraulicsAngle == 0:                                # If the gear is retracted enough
                self.state = GearState.DOWN_LOCKED
                logWrite.info("Gear Retracted")
            else:                                                   # If the gear is not retracted enough
                logWrite.warning("Insufficient Gear Retraction angle")
        else:
            logWrite.warning("Command Rejected")

debug = False                                                        # Sets the debug of the script t/f
timeControls = False
Hydraulics = HydraulicActuators                                     # Creates an object of the class Hydraulics
Hydraulics.temperature = 30 
HydraulicActuators.refreshEfficiency(Hydraulics, 80, 500)           # Calculates the hydraulic efficiency

controller = LandingGearController()
controller.command_gear_down()
controller.command_gear_up()