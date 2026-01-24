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

#Writes logs with additional information when active
def hydraulicDebug(self, timePeriod):
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

def runRandomFaultHydraulics():
    if randomFaultsHydraulics > 0:
        if randint(randomFaultsHydraulics, 10000) == 10000:
            Hydraulics.fault = True

def runRandomFaultSensors(sensor):
    if randomFaultSensors > 0:
        if randint(randomFaultSensors, 1000) == 1000:
            if sensor.condition == sensorState.faulty or randint(1,5) == 5:
                sensor.condition = sensorState.broken
            else:
                sensor.condition = sensorState.faulty

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

#Defines the sensor class
class sensors:
    condition = sensorState.functional

    #Defines how the sensor reacts in different states
    def read(self):
        if self.condition == sensorState.functional:
            angle = Hydraulics.angle
        elif self.condition == sensorState.faulty:
            angle = Hydraulics.angle + (randint(-100, 100) / 10)
        elif self.condition == sensorState.broken:
            angle = -1
        
        runRandomFaultSensors(self)
        return angle

#Defines the Hydraulic Class
class HydraulicActuators:
    temperature = 30
    angle = 0
    fault = False
    efficiency = 0.10

    #Calculates the efficiency- how fast the hydraulics work
    def refreshEfficiency(self, windMPH, altitudeFT): 
        self.efficiency = (0.10 - (windMPH * 0.00007)) - (altitudeFT * 0.000005)
        if self.temperature < -20:
            self.efficiency *= 0.8
        elif self.temperature > 80:
            self.efficiency *= 0.9
        
        if self.efficiency < 0:
            self.efficiency = 0
    
    #Extends the hydraulics by time and efficiency
    def extending(self, timePeriod):
        temp = timePeriod
        for t in range (0,temp): 
            runRandomFaultHydraulics()
            if self.fault == False:  
                timePause(0.01)                         # causes a real time simulation delay
                timePeriod -= 1
                self.angle += self.efficiency
                if self.angle >= 90:                        # stops extending at 90 degrees
                    self.angle = 90
                    break
            else:
                logWrite.warning("Hydraulic Fault Detected")
                break
        hydraulicDebug (self, timePeriod)
        return self.angle, timePeriod                   # returns the extended angle and time


    #Retracts the hydraulics by time and efficiency
    def retracting(self, timePeriod):
        temp = timePeriod
        for t in range (0,temp):
            runRandomFaultHydraulics()
            if self.fault == False:
                timePause (0.01)                            # causes a real time simulation delay
                timePeriod -= 1
                self.angle -= self.efficiency
                if round(self.angle, 3) <= 0:                        # stops retracting at 0 degrees
                    self.angle = 0
                    break
            else:
                logWrite.warning("Hydraulic Fault Detected") 
                break
        hydraulicDebug (self, timePeriod)
        return self.angle, timePeriod                           # returns the extended angle and time
                 

#Defines the controller which will interact with the rest of the system
class LandingGearController:
    def __init__(self):
        self.state = GearState.UP_LOCKED

    #Attempts to move the gear into the extended position
    def command_gear_down(self):
        if windSpeed < 250:
            sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
            if sensorReading != -1:
                if sensorReading < 90:                                  # Confirms the gear is in a valid position                     
                    self.state = GearState.TRANSITIONING_DOWN
                    logWrite.info("Deploying")
                    HydraulicActuators.extending(Hydraulics, 1200) # Calls the hydraulics to move
                    sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
                    if sensorReading == 90:                               # If the gear does extend enough
                        self.state = GearState.DOWN_LOCKED
                        logWrite.info("Gear Deployed")
                    elif sensorReading == -1:
                        logWrite.critical("Two Or More Sensors Have Fault - Unable To Verify Gear Poistion")
                    else:                                                   # If the gear does not extend enough
                        logWrite.warning("Insufficient Gear Deployment angle - under 90")
                        self.state = GearState.STATIONARY_LOCKED
                else:
                    logWrite.warning("Command Rejected - Already Deployed")
            else:
                logWrite.critical("Two Or More Sensors Have Fault - Unable To Verify Gear Poistion")
        else:
            logWrite.warning("Command Rejected - Dangerous windSpeed ")
        
    #Attempts to move the gear into the retracted position
    def command_gear_up(self):
        if windSpeed < 250:
            sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
            if sensorReading > -1: 
                if sensorReading > 0:        # Confirms the gear is in a valid position
                    self.state = GearState.TRANSITIONING_UP
                    logWrite.info("Retracting")
                    HydraulicActuators.retracting(Hydraulics, 1200) # Calls the hydraulics to move
                    sensorReading = sensorDataView (sensor1.read(), sensor2.read(), sensor3.read())
                    if sensorReading == 0:                                # If the gear is retracted enough
                        self.state = GearState.UP_LOCKED
                        logWrite.info("Gear Retracted")
                    elif sensorReading == -1:
                        logWrite.critical("Two Or More Sensors Have Fault - Unable To Verify Gear Poistion")
                    else:                                                   # If the gear is not retracted enough
                        logWrite.warning("Insufficient Gear Retraction angle - above 0")
                        self.state = GearState.STATIONARY_LOCKED
                else:
                    logWrite.warning("Command Rejected - Already Retracted")
            else:
                logWrite.critical("Two Or More Sensors Have Fault - Unable To Verify Gear Poistion")
        else:
            logWrite.warning("Command Rejected - Dangerous windSpeed ")

#Validates sensor date
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
        

# Creates an object of the class Hydraulics
Hydraulics = HydraulicActuators()

#Set runtime parameters
debug = False                                                       
timeControls = False  
randomFaultsHydraulics = 100 # The chance of developing a fault - 0 is off, 1-10000 - Max is gaurenteed 
randomFaultSensors = 10  # The chance of developing a fault - 0 is off, 1-1000 - Max is gaurenteed 

Hydraulics.temperature = 37
windSpeed = 200
altitude = 1500

#Defining attributes
HydraulicActuators.refreshEfficiency(Hydraulics, windSpeed, altitude)           
controller = LandingGearController()
sensor1 = sensors()
sensor2 = sensors()
sensor3 = sensors()

#Change sensor states
#sensor1.condition = sensorState.faulty
#sensor2.condition = sensorState.broken

#Commands sent to the gear system
controller.command_gear_down()
controller.command_gear_up()
controller.command_gear_up()