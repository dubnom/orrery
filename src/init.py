from tic import *


# Discover the ticID
tics = TicList()
if len(tics) == 0:
    print("No TIC motor controller found.")
    exit(0)
elif len(tics) > 1:
    print("Too many TIC motor controllers found.")
    exit(0)
ticID = tics[0][0]

# Connect to the TIC
tic = TicController(ticID)
if not tic:
    print(f"TIC motor controller couldn't be found '{ticID}'")
    exit(0)

# Set the orrery default parameters
if False:
    tic.settingSetMaxAcceleration(20000)
    tic.settingSetMaxDeceleration(0)
    tic.settingSetMaxSpeed(32000000)
    tic.settingSetCurrentLimit(t500_lookupCurrent(.500))
    tic.settingSetStepMode(STEP_MODE_8)
    tic.settingSetInvertMotorDirection(1)
    tic.settingSetCommandTimeout(0)

print("Max Acceleration:", tic.settingGetMaxAcceleration())
print("Max Deceleration:", tic.settingGetMaxDeceleration())
print("Max Speed:", tic.settingGetMaxSpeed())
print("Current Limit:", T500_CURRENTS[tic.settingGetCurrentLimit()])
print("Step Mode:", tic.settingGetStepMode())
print("Invert Motor Direction:", tic.settingGetInvertMotorDirection())
print("Command Timeout:", tic.settingGetCommandTimeout())

print("Done!")


