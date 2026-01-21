from enum import Enum, auto
from random import randint
import time

class GearState(Enum):
    UP_LOCKED = auto()
    TRANSITIONING_UP = auto()

    DOWN_LOCKED = auto()
    TRANSITIONING_DOWN = auto()

class LandingGearController:
    def __init__(self):
        self.state = GearState.UP_LOCKED

    def log(self, message):
        print(f"[{self.state.name}] {message}")

    def command_gear_down(self):
        if self.state == GearState.UP_LOCKED:
            self.state = GearState.TRANSITIONING_DOWN
            self.log("Gear Deploying")
            time.sleep(1)
            self.log("Gear Deployed")
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

controller = LandingGearController()
controller.command_gear_down()
controller.command_gear_up()