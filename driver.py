import msgParser
import carState
import carControl
import csv
import keyboard 

class Driver(object):
    '''
    A driver object for the SCRC
    '''

    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage
        
        self.parser = msgParser.MsgParser()
        self.state = carState.CarState()
        self.control = carControl.CarControl()
        
        self.steer_lock = 0.785398
        self.max_speed = 100
        self.prev_rpm = None

        # Initialize the telemetry log
        self.log_file = open("telemetry_log.csv", "wb")  # Python 2 compatibility
        self.logger = csv.writer(self.log_file)
        self.logger.writerow([
            "time", "speedX", "speedY", "speedZ", "trackPos", 
            "angle", "gear", "rpm", "acceleration", "brake", "steer",
            "distFromStart", "distRaced", "racePos", "track", 
            "wheelSpinVel", "z"
        ])

    def logTelemetry(self):
        '''Log relevant telemetry data including additional sensor values'''
        self.logger.writerow([
            self.state.getCurLapTime(),    # time
            self.state.getSpeedX(),
            self.state.getSpeedY(),
            self.state.getSpeedZ(),
            self.state.getTrackPos(),
            self.state.getAngle(),
            self.state.getGear(),
            self.state.getRpm(),
            self.control.getAccel(),
            self.control.getBrake(),
            self.control.getSteer(),
            self.state.getDistFromStart(),
            self.state.getDistRaced(),
            self.state.getRacePos(),
            self.state.getTrack(),
            self.state.getWheelSpinVel(),
            self.state.getZ()
        ])

    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]
        
        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15
        
        for i in range(5, 9):
            self.angles[i] = -20 + (i-5) * 5
            self.angles[18 - i] = 20 - (i-5) * 5
        
        return self.parser.stringify({'init': self.angles})
    
 
    def drive(self, msg):

        print("Drive function called!")  # Debugging print
        self.state.setFromMsg(msg)

        # Log telemetry data
        self.logTelemetry()

        # Manual control using keyboard input.
        # Acceleration control: 
        #   W key for full throttle,
        #   S key for braking (zero acceleration).
        if keyboard.is_pressed('w'):
            self.control.setAccel(0.6)
        elif keyboard.is_pressed('s'):
            self.control.setAccel(0.0)
        else:
            # If no key is pressed, set acceleration to 0.
            self.control.setAccel(0.0)

        # Steering control:
        #   A key for full left, 
        #   D key for full right.
        if keyboard.is_pressed('a'):
            self.control.setSteer(self.steer_lock)
        elif keyboard.is_pressed('d'):
            self.control.setSteer(-self.steer_lock)
        else:
            self.control.setSteer(0.0)

        # For manual control, we fix the gear to 1.
        self.control.setGear(1)

        print("Manual Control - Accel:", self.control.getAccel(), "Steer:", self.control.getSteer())  # Debugging print
        print("Current Speed:", self.state.getSpeedX())  # Debugging print
        self.gear()
        return self.control.toMsg()
    
    def steer(self):
        angle = self.state.getAngle()
        dist = self.state.getTrackPos()
        
        # Adjust steering sensitivity
        steer_value = (angle - dist * 0.2) / self.steer_lock  # Reduced effect of distance
        steer_value = max(-1, min(1, steer_value))  # Clamp values

        self.control.setSteer(steer_value)
        print("Steering:", steer_value)  # Debugging print
    
    def gear(self):
        rpm = self.state.getRpm()
        gear = self.state.getGear()

        if self.prev_rpm is None:
            self.prev_rpm = rpm  # Initialize previous RPM

        # Shift up if RPM is too high
        if rpm > 7000 and gear < 6:
            gear += 1

        # Shift down if RPM is too low and gear is not 1
        elif rpm < 2500 and gear > 1:
            gear -= 1

        # Ensure we never stay in neutral (0)
        if gear == 0:
            gear = 1

        self.control.setGear(gear)
        self.prev_rpm = rpm  # Update previous RPM
        print("Gear:", gear, "RPM:", rpm)  # Debugging print
    
    def speed(self):
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()

        # Smooth acceleration control
        if speed < self.max_speed:
            accel = min(accel + 0.1, 1.0)  # Gradual increase
        else:
            accel = max(accel - 0.05, 0.1)  # Reduce speed gradually, not abruptly

        self.control.setAccel(accel)
        print("Speed:", speed, "Acceleration:", accel)  # Debugging print
            
    def onShutDown(self):
        '''Close the telemetry log file on shutdown'''
        self.log_file.close()
    
    def onRestart(self):
        pass
