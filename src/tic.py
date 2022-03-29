import struct
import usb
import bisect

# Planning mode
PLANNING_MODE_OFF       = 0
PLANNING_MODE_POSITION  = 1
PLANNING_MODE_VELOCITY  = 2

# Number of partial steps
STEP_MODE_1     = 0
STEP_MODE_2     = 1
STEP_MODE_4     = 2
STEP_MODE_8     = 3
STEP_MODE_16    = 4
STEP_MODE_32    = 5
STEP_MODE_2_100 = 6
STEP_MODE_64    = 7
STEP_MODE_128   = 8
STEP_MODE_256   = 9

# Decay modes vary by driver
DECAY_MODE_T500_AUTO    = 0

DECAY_MODE_T834_MIX_50  = 0
DECAY_MODE_T834_SLOW    = 1
DECAY_MODE_T834_FAST    = 2
DECAY_MODE_T834_MIX_25  = 3
DECAY_MODE_T834_MIX_75  = 4

DECAY_MODE_T825_MIX     = 0
DECAY_MODE_T825_SLOW    = 1
DECAY_MODE_T825_FAST    = 2

DECAY_MODE_T249_MIX     = 0

# Input states
INPUT_STATE_NOT_READY   = 0
INPUT_STATE_INVALID     = 1
INPUT_STATE_HALT        = 2
INPUT_STATE_TARGET_POS  = 3
INPUT_STATE_TARGET_VOL  = 4

# Motor driver errors
MOTOR_ERROR_NONE        = 0
MOTOR_ERROR_CURRENT     = 1
MOTOR_ERROR_TEMPERATURE = 2

# High-Power motor driver error bits
HP_ERROR_OVERTEMP       = 0x01
HP_ERROR_OVERCURRENT_A  = 0x02
HP_ERROR_OVERCURRENT_B  = 0x04
HP_ERROR_PREDRIVER_A    = 0x08
HP_ERROR_PREDRIVER_B    = 0x10
HP_ERROR_UNDERVOLTAGE   = 0x20
HP_ERROR_VERIFICATION   = 0x80

# Control modes
CONTROL_MODE_SERIAL_I2C_USB     = 0
CONTROL_MODE_STEP_DIR           = 1
CONTROL_MODE_RC_POSITION        = 2
CONTROL_MODE_RC_SPEED           = 3
CONTROL_MODE_ANALOG_POSITION    = 4
CONTROL_MODE_ANALOG_SPEED       = 5
CONTROL_MODE_ENCODER_POSITION   = 6
CONTROL_MODE_ENCODER_SPEED      = 7

# Settings
ST_NOT_INITIALIZED          = 0x00
ST_CONTROL_MODE             = 0x01
ST_NEVER_SLEEP              = 0x02
ST_DISABLE_SAFE_START       = 0x03
ST_IGNORE_ERR_LINE_HIGH     = 0x04
ST_SERIAL_BAUD_RATE         = 0x05
ST_SERIAL_DEVICE_NUMBER_L   = 0x07
ST_AUTO_CLEAR_DRIVER_ERRORS = 0x08
ST_COMMAND_TIMEOUT          = 0x09
ST_SERIAL_FLAGS             = 0x0B
ST_VIN_CALIBRATION          = 0x14
ST_INVERT_MOTOR_DIRECTION   = 0x1B
ST_INPUT_SCALING_DEGREE     = 0x20
ST_INVERT_INPUT_DIRECTION   = 0x21
ST_INPUT_MINIMUM            = 0x22
ST_INPUT_NEUTRAL_MIN        = 0x24
ST_INPUT_NEUTRAL_MAX        = 0x26
ST_INPUT_MAXIMUM            = 0x28
ST_TARGET_MINIMUM           = 0x2A
ST_INPUT_HYSTERESIS         = 0x2F
ST_CURRENT_LIMIT_DURING_ERR = 0x31
ST_TARGET_MAXIMUM           = 0x32
ST_SWITCH_POLARITY_MAP      = 0x36
ST_ENCODER_POSTSCALER       = 0x37
ST_SCL_PIN_CONFIGURATION    = 0x3B
ST_SDA_PIN_CONFIGURATION    = 0x3C
ST_TX_PIN_CONFIGURATION     = 0x3D
ST_RX_PIN_CONFIGURATION     = 0x3E
ST_RC_PIN_CONFIGURATION     = 0x3F
ST_CURRENT_LIMIT            = 0x40
ST_STEP_MODE                = 0x41
ST_DECAY_MODE               = 0x42
ST_MAX_SPEED                = 0x47
ST_STARTING_SPEED           = 0x43
ST_MAX_ACCELERATION         = 0x4F
ST_MAX_DECELERATION         = 0x4B
ST_SOFT_ERROR_RESPONSE      = 0x53
ST_SOFT_ERROR_POSITION      = 0x54
ST_ENCODER_PRESCALER        = 0x58
ST_ENABLE_UNBOUND_POSITION  = 0x5C
ST_KILL_SWITCH_MAP          = 0x5D
ST_SERIAL_RESPONSE_DELAY    = 0x5E
ST_LIMIT_SWITCH_FORWARD_MAP = 0x5F
ST_LIMIT_SWITCH_REVERSE_MAP = 0x60
ST_HOMING_SPEED_AWAY        = 0x65
ST_SERIAL_DEVICE_NUMBER_H   = 0x69
ST_ENABLE_ALT_DEV_NUMBER    = 0x6A
ST_SERIAL_ALT_DEV_NUMBER_L  = 0x6A
ST_SERIAL_ALT_DEV_NUMBER_H  = 0x6B
ST_AGC_MODE                 = 0x6C
ST_AGC_BOTTOM_CURRENT_LIMIT = 0x6D
ST_AGC_CURRENT_BOOST_STEPS  = 0x6E
ST_AGC_FREQUENCY_LIMIT      = 0x6F

# Controller variable indices
VAR_OPERATION_STATE             = 0x00
VAR_MISC_FLAGS                  = 0x01
VAR_ERROR_STATUS                = 0x02
VAR_ERRORS_OCCURRED             = 0x04
VAR_PLANNING_MODE               = 0x09
VAR_TARGET_POSITION             = 0x0A
VAR_TARGET_VELOCITY             = 0x0E
VAR_STARTING_SPEED              = 0x12
VAR_MAX_SPEED                   = 0x16
VAR_MAX_DECELERATION            = 0x1A
VAR_MAX_ACCELERATION            = 0x1E
VAR_CURRENT_POSITION            = 0x22
VAR_CURRENT_VELOCITY            = 0x26
VAR_ACTING_TARGET_POSITION      = 0x2A
VAR_TIME_SINCE_LAST_STEP        = 0x2E
VAR_DEVICE_RESET                = 0x32
VAR_VIN_VOLTAGE                 = 0x33
VAR_UP_TIME                     = 0x35
VAR_ENCODER_POS                 = 0x39
VAR_RC_PULSE_WIDTH              = 0x3D
VAR_ANALOG_READING_SCL          = 0x3F
VAR_ANALOG_READING_SDA          = 0x41
VAR_ANALOG_READING_TX           = 0x43
VAR_ANALOG_READING_RX           = 0x45
VAR_DIGITAL_READINGS            = 0x47
VAR_PIN_STATES                  = 0x48
VAR_STEP_MODE                   = 0x49
VAR_CURRENT_LIMIT               = 0x4A
VAR_DECAY_MODE                  = 0x4B
VAR_INPUT_STATE                 = 0x4C
VAR_INPUT_AFTER_AVG             = 0x4D
VAR_INPUT_AFTER_HYST            = 0x4F
VAR_INPUT_AFTER_SCALING         = 0x51
VAR_LAST_MOTOR_DRIVER_ERROR     = 0x55
VAR_AGC_MODE                    = 0x56
VAR_AGC_BOTTOM_CURRENT_LIMIT    = 0x57
VAR_AGC_CURRENT_BOOST_STEPS     = 0x58
VAR_AGC_FREQ_LIMIT              = 0x59
VAR_LAST_HP_DRIVER_ERRORS       = 0xFF

# USB Vendor information
ID_POLOLU   = 0x1ffb
PROD_TIC500 = 0x00bd
PROD_TIC249 = 0x00c9

# Current lookup table for the T500 driver
T500_CURRENTS = [
    0, .1, .174, .343, .495, .634, .762, .880,
    .990, 1.092, 1.189, 1.281, 1.368, 1.452, 1.532, 1.611,
    1.687, 1.762, 1.835, 1.909, 1.982, 2.056, 2.131, 2.207,
    2.285, 2.366, 2.451, 2.540, 2.634, 2.734, 2.843, 2.962, 3.093
]

def t500_lookupCurrent(current):
    return bisect.bisect_right(T500_CURRENTS, current) - 1

def TicList():
    """Return a list of devices made by Pololu."""
    return [ (dev.serial_number,dev.product,dev.idProduct) for dev in usb.core.find(find_all=True, idVendor=ID_POLOLU)]


class TicController(object):
    """Interface to Tic stepper motor controllers."""

    def __init__(self, serialNumber):
        dev = usb.core.find(idVendor=0x1ffb, serial_number=serialNumber)
        dev.set_configuration()
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        self._dev = dev

    def _quick(self, command):
        self._dev.ctrl_transfer(0x40, command, 0, 0, None)

    def _write7(self, command, data):
        self._dev.ctrl_transfer(0x40, command, data, 0, 0, None)

    def _write32(self, command, data):
        self._dev.ctrl_transfer(0x40, command, data & 0xffff, data >> 16, 0, None)

    def _writes32(self, command, data):
        buf = bytearray(struct.pack("<i", data))
        self._dev.ctrl_transfer(0x40, command, (buf[1]<<8) | buf[0], (buf[3]<<8) | buf[2], 0, None)

    def _blockRead(self, command, offset, length):
        return self._dev.ctrl_transfer(0xC0, command, 0, offset, length)

    def _read8(self, command, offset):
        buf = self._blockRead(command, offset, 1)
        return struct.unpack("<B", buf)[0]

    def _read16(self, command, offset):
        buf = self._blockRead(command, offset, 2)
        return struct.unpack("<H", buf)[0]

    def _read32(self, command, offset):
        buf = self._blockRead(command, offset, 4)
        return struct.unpack("<I", buf)[0]

    def _reads32(self, command, offset):
        buf = self._blockRead(command, offset, 4)
        return struct.unpack("<i", buf)[0]

    def _set8(self, offset, data):
        self._dev.ctrl_transfer(0x40, 0x13, data & 0x00ff, offset, 0, None)

    def _set16(self, offset, data):
        self._set8(offset, data & 0xff)
        self._set8(offset+1, data >> 8)

    def _set32(self, offset, data):
        self._set16(offset, data & 0xffff)
        self._set16(offset+2, data >> 16)


    def setTargetPosition(self, position):          self._writes32(0xE0, position)
    def setTargetVelocity(self, velocity):          self._write32(0xE3, velocity)
    def haltAndSetPosition(self, position):         self._writes32(0xEC, position)
    def haltAndHold(self):                          self._quick(0x89)
    def goHomeForward(self):                        self._write7(0x97, 1)
    def goHomeReverse(self):                        self._write7(0x97, 0)
    def resetCommandTimeout(self):                  self._quick(0x8C)
    def deenergize(self):                           self._quick(0x86)
    def energize(self):                             self._quick(0x85)
    def exitSafeStart(self):                        self._quick(0x83)
    def enterSafeStart(self):                       self._quick(0x8F)
    def reset(self):                                self._quick(0xB0)
    def clearDriverError(self):                     self._quick(0x8A)
    def setMaxSpeed(self, speed):                   self._write32(0xE6, speed)
    def setStartingSpeed(self, speed):              self._write32(0xE5, speed)
    def setMaxAcceleration(self, accel):            self._write32(0xEA, accel)
    def setMaxDeceleration(self, decel):            self._write32(0xE9, decel)
    def setStepMode(self, mode):                    self._write7(0x94, mode)
    def setCurrentLimit(self, limit):               self._write7(0x91, limit)
    def setDecayMode(self, mode):                   self._write7(0x92, mode)
    def setAGCOption(self, option):                 self._write7(0x98, option)
    def reinitialize(self):                         self._quick(0x10)


    def getOperationState(self):        return self._read8(0xA1, VAR_OPERATION_STATE)
    def getMiscFlags(self):             return self._read8(0xA1, VAR_MISC_FLAGS)
    def getErrorStatus(self):           return self._read16(0xA1, VAR_ERROR_STATUS)
    def getErrorsOccurred(self):        return self._read32(0xA1, VAR_ERRORS_OCCURRED)
    def getPlanningMode(self):          return self._read8(0xA1, VAR_PLANNING_MODE)
    def getTargetPosition(self):        return self._reads32(0xA1, VAR_TARGET_POSITION)
    def getTargetVelocity(self):        return self._read32(0xA1, VAR_TARGET_VELOCITY)
    def getStartingSpeed(self):         return self._read32(0xA1, VAR_STARTING_SPEED)
    def getMaxSpeed(self):              return self._read32(0xA1, VAR_MAX_SPEED)
    def getMaxDeceleration(self):       return self._read32(0xA1, VAR_MAX_DECELERATION)
    def getMaxAcceleration(self):       return self._read32(0xA1, VAR_MAX_ACCELERATION)
    def getCurrentPosition(self):       return self._reads32(0xA1, VAR_CURRENT_POSITION)
    def getCurrentVelocity(self):       return self._read32(0xA1, VAR_CURRENT_VELOCITY)
    def getActingTargetPosition(self):  return self._reads32(0xA1, VAR_ACTING_TARGET_POSITION)
    def getTimeSinceLastStep(self):     return self._read32(0xA1, VAR_TIME_SINCE_LAST_STEP)
    def getDeviceReset(self):           return self._read8(0xA1, VAR_DEVICE_RESET)
    def getVINVoltage(self):            return 0.001 * self._read16(0xA1, VAR_VIN_VOLTAGE)
    def getUpTime(self):                return self._read32(0xA1, VAR_UP_TIME)
    def getEncoderPos(self):            return self._reads32(0xA1, VAR_ENCODER_POS)
    def getRCPulseWidth(self):          return self._read16(0xA1, VAR_RC_PULSE_WIDTH)
    def getAnalogReadingSCL(self):      return self._read16(0xA1, VAR_ANALOG_READING_SCL)
    def getAnalogReadingSDA(self):      return self._read16(0xA1, VAR_ANALOG_READING_SDA)
    def getAnalogReadingTX(self):       return self._read16(0xA1, VAR_ANALOG_READING_TX)
    def getAnalogReadingRX(self):       return self._read16(0xA1, VAR_ANALOG_READING_RX)
    def getDigitalReadings(self):       return self._read8(0xA1, VAR_DIALOG_READINGS)
    def getPinStates(self):             return self._read8(0xA1, VAR_PIN_STATES)
    def getStepMode(self):              return self._read8(0xA1, VAR_STEP_MODE)
    def getCurrentLimit(self):          return self._read8(0xA1, VAR_CURRENT_LIMIT)
    def getDecayMode(self):             return self._read8(0xA1, VAR_DECAY_MODE)
    def getInputState(self):            return self._read8(0xA1, VAR_INPUT_STATE)
    def getInputAfterAvg(self):         return self._read16(0xA1, VAR_INPUT_AFTER_AVG)
    def getInputAfterHyst(self):        return self._read16(0xA1, VAR_INPUT_AFTER_HYST)
    def getInputAfterScaling(self):     return self._read32(0xA1, VAR_INPUT_AFTER_SCALING)
    def getLastMotorDriverError(self):  return self._read8(0xA1, VAR_LAST_MOTOR_DRIVER_ERROR)
    def getAGCMode(self):               return self._read8(0xA1, VAR_AGC_MODE)
    def getAGCBottomCurrentLimit(self): return self._read8(0xA1, VAR_AGC_BOTTOM_CURRENT_LIMIT)
    def getAGCCurrentBoostSteps(self):  return self._read8(0xA1, VAR_AGC_CURRENT_BOOST_STEPS)
    def getAGCFreqLimit(self):          return self._read8(0xA1, VAR_AGC_FREQ_LIMIT)
    def getLastHPDriverErrors(self):    return self._read8(0xA1, VAR_LAST_HP_DRIVER_ERRORS)

    def settingGetControlMode(self):            return self._read8(0xA8, ST_CONTROL_MODE)
    def settingGetCommandTimeout(self):         return self._read16(0xA8, ST_COMMAND_TIMEOUT)
    def settingGetSerialBaudRate(self):         return self._read16(0xA8, ST_SERIAL_BAUD_RATE)
    def settingGetCurrentLimit(self):           return self._read8(0xA8, ST_CURRENT_LIMIT)
    def settingGetInvertMotorDirection(self):   return self._read8(0xA8, ST_INVERT_MOTOR_DIRECTION)
    def settingGetMaxAcceleration(self):        return self._read32(0xA8, ST_MAX_ACCELERATION)
    def settingGetMaxDeceleration(self):        return self._read32(0xA8, ST_MAX_DECELERATION)
    def settingGetMaxSpeed(self):               return self._read32(0xA8, ST_MAX_SPEED)
    def settingGetStepMode(self):               return self._read8(0xA8, ST_STEP_MODE)

    def settingSetControlMode(self, mode):          self._set8(ST_CONTROL_MODE, mode)
    def settingSetCommandTimeout(self, timeout):    self._set16(ST_COMMAND_TIMEOUT, timeout)
    def settingSetSerialBaudRate(self, baud):       self._set16(ST_SERIAL_BAUD_RATE, baud)
    def settingSetCurrentLimit(self, limit):        self._set8(ST_CURRENT_LIMIT, limit)
    def settingSetInvertMotorDirection(self, flag): self._set8(ST_INVERT_MOTOR_DIRECTION, flag)
    def settingSetMaxAcceleration(self, rate):      self._set32(ST_MAX_ACCELERATION, rate)
    def settingSetMaxDeceleration(self, rate):      self._set32(ST_MAX_DECELERATION, rate)
    def settingSetMaxSpeed(self, speed):            self._set32(ST_MAX_SPEED, speed)
    def settingSetStepMode(self, mode):             self._set8(ST_STEP_MODE, mode)

