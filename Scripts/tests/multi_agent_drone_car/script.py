import time
import os
import tempfile

from cosysairsim.client import CarClient, MultirotorClient
from cosysairsim.types import CarControls

# —————————————————————————————————————————————
# Configuration — update if needed
DRONE_PORT = 41451
CAR_PORT   = 41452

# Temporary directory for images
TMP_DIR = os.path.join(tempfile.gettempdir(), "cosysairsim_output")

os.makedirs(TMP_DIR, exist_ok=True)

# —————————————————————————————————————————————
# Connect to the CosysAirSim API
drone_client = MultirotorClient(port=DRONE_PORT)
drone_client.confirmConnection()
drone_client.enableApiControl(True, vehicle_name="Drone1")
drone_client.armDisarm(arm=True, vehicle_name="Drone1")

car_client   = CarClient(port=CAR_PORT)
car_client.confirmConnection()
car_client.enableApiControl(True, vehicle_name= "Car1")
car_controls = CarControls()

# —————————————————————————————————————————————
# Takeoff Drone
f1 = drone_client.takeoffAsync(vehicle_name="Drone1")
print("Drone1: Taking off…")
car_state1 = car_client.getCarState("Car1")
print("Car1: Speed %d, Gear %d" % (car_state1.speed, car_state1.gear))
f1.join()
state1 = drone_client.getMultirotorState(vehicle_name="Drone1")

# —————————————————————————————————————————————
# Optional Movement (commented out)
f1 = drone_client.moveToPositionAsync(-5, 5, -10, 5, vehicle_name="Drone1")
car_controls.throttle = 0.5
car_controls.steering = 0.5
car_client.setCarControls(car_controls, vehicle_name="Car1")
print("Car1: Moving forward…")
f1.join()
time.sleep(2)

print("Car1: Braking…")
car_controls.throttle = 0.0
car_controls.steering = 0.0
car_controls.brake = 1.0
car_client.setCarControls(car_controls, vehicle_name="Car1")
time.sleep(2)

# —————————————————————————————————————————————
# Reset vehicles
drone_client.armDisarm(arm=False, vehicle_name="Drone1")
drone_client.reset()
car_client.reset()

# —————————————————————————————————————————————
# Disable API Control
drone_client.enableApiControl(False, vehicle_name="Drone1")
car_client.enableApiControl(False, vehicle_name="Car1")

print("Finished.")