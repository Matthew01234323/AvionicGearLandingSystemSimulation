from enum import Enum, auto
from random import randint
import time
import logging as logWrite

logWrite.basicConfig(
    filename = "simulationLog",
    filemode = "w",
    level = logWrite.INFO,
    format = "%(asctime)s - %(levelname)s : %(message)s",
    datefmt= "%H:%M:%S"
    )

def hydraulicDebug(self, timePeriod):                                           # Provides Log feedback
    if debug == True:
        message = "time left:"+ str(timePeriod*10) + "ms"
        logWrite.info (message)
        message = "efficiency:"+ str(int(self.efficiency * 1000)) + "%"
        logWrite.info (message)

        message = "angle:"+ str(round(self.angle, 3))
        logWrite.info (message)

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

class sensorState(Enum):
    functional = auto()
    faulty = auto()
    broken = auto()

class sensors:
    condition = sensorState.functional

    def read(self):
        if self.condition == sensorState.functional:
            angle = Hydraulics.angle
        elif self.condition == sensorState.faulty:
            angle = Hydraulics.angle + (randint(-100, 100) / 10)
        elif self.condition == sensorState.broken:
            angle = -1

        return angle

class HydraulicActuators:
    temperature = 30
    angle = 0
    fault = False
    efficiency = 0.10

    def refreshEfficiency(self, windMPH, altitudeFT):       # Calculates the efficiency of the hydraulics
        self.efficiency = (0.10 - (windMPH * 0.00007)) - (altitudeFT * 0.000005)
        if self.temperature < -20:
            self.efficiency *= 0.8
        elif self.temperature > 80:
            self.efficiency *= 0.9
        
        if self.efficiency < 0:
            self.efficiency = 0
        
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
        else:
            logWrite.warning("Hydraulic Fault Detected")

    def retracting(self, timePeriod):
        if self.fault == False:
            temp = timePeriod
            for t in range (0,temp):
                timePause (0.01)                            # causes a real time simulation delay
                timePeriod -= 1
                self.angle -= self.efficiency
                if round(self.angle, 3) <= 0:                        # stops extending at 90 degrees
                    self.angle = 0
                    break
            hydraulicDebug (self, timePeriod)
            return self.angle, timePeriod                           # returns the extended angle and time
        else:
            logWrite.warning("Hydraulic Fault Detected")                  

class LandingGearController:
    def __init__(self):
        self.state = GearState.UP_LOCKED

    def command_gear_down(self):
        if windSpeed < 250:
            sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
            if sensorReading != -1:
                if sensorReading < 90:                                  # Confirms the gear is in a valid position                     
                    self.state = GearState.TRANSITIONING_DOWN
                    logWrite.info("Gear Deploying")
                    HydraulicActuators.extending(Hydraulics, 1200) # Calls the hydraulics to move
                    sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
                    if sensorReading == 90:                               # If the gear does extend enough
                        self.state = GearState.DOWN_LOCKED
                        logWrite.info("Gear Deployed")
                    else:                                                   # If the gear does not extend enough
                        logWrite.warning("Insufficient Gear Deployment angle - under 90")
                        self.state = GearState.STATIONARY_LOCKED
                else:
                    logWrite.warning("Command Rejected - Already Deployed")
            else:
                logWrite.critical("Two Or More Sensors Have Fault - Unable To Verify Gear Poistion")
        else:
            logWrite.warning("Command Rejected - Dangerous windSpeed ")
        
    def command_gear_up(self):
        if windSpeed < 250:
            sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
            if sensorReading > -1: 
                if sensorReading > 0:        # Confirms the gear is in a valid position
                    self.state = GearState.TRANSITIONING_UP
                    logWrite.info("Gear Retracting")
                    HydraulicActuators.retracting(Hydraulics, 1200) # Calls the hydraulics to move
                    sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
                    if sensorReading == 0:                                # If the gear is retracted enough
                        self.state = GearState.UP_LOCKED
                        logWrite.info("Gear Retracted")
                    else:                                                   # If the gear is not retracted enough
                        logWrite.warning("Insufficient Gear Retraction angle - above 0")
                        self.state = GearState.STATIONARY_LOCKED
                else:
                    logWrite.warning("Command Rejected - Already Retracted")
            else:
                logWrite.critical("Two Or More Sensors Have Fault - Unable To Verify Gear Poistion")
        else:
            logWrite.warning("Command Rejected - Dangerous windSpeed ")

def sensorDataView (s1, s2, s3):
    if s1 == s2 and s2 == s3:
        return s1
    else:
        if s1 == s2:
            return s1
        if s1 == s3:
            return s1
        if s2 == s3:
            return s2
        
        return -1
        
sensor1 = sensors()
sensor2 = sensors()
sensor3 = sensors()

#sensor1.condition = sensorState.faulty
#sensor2.condition = sensorState.faulty

Hydraulics = HydraulicActuators()                                  # Creates an object of the class Hydraulics
Hydraulics.temperature = 37
Hydraulics.fault = False
windSpeed = 200
altitude = 1500

#print (sensorDataView (sensor1.read(), sensor2.read(), sensor3.read()))

debug = False                                                        # Sets the debug of the script t/f
timeControls = False                                                 # Sets the real time simulation t/f

HydraulicActuators.refreshEfficiency(Hydraulics, windSpeed, altitude)           # Calculates the hydraulic efficiency

controller = LandingGearController()
controller.command_gear_down()
controller.command_gear_up()
controller.command_gear_up()