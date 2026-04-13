import time

from cosysairsim.client import CarClient, MultirotorClient
from cosysairsim.types import CarControls

# —————————————————————————————————————————————
# Configuration
DRONE_PORT = 41451
CAR_PORT   = 41452

# —————————————————————————————————————————————
# Connect to the CosysAirSim API
drone_client = MultirotorClient(port=DRONE_PORT)
drone_client.confirmConnection()
drone_client.enableApiControl(True, vehicle_name="Drone1")
# We intentionally do NOT arm or move the drone. It will just sit on the ground.

car_client = CarClient(port=CAR_PORT)
car_client.confirmConnection()
car_client.enableApiControl(True, vehicle_name="Car1")
car_controls = CarControls()

# —————————————————————————————————————————————
# 1. Setup the Scene
print("Drone1: Sitting completely still on the ground as an obstacle...")
print("Car1: Full throttle ahead! Preparing to run over the drone...")

# 2. Initiate the Crash (Car)
car_controls.throttle = 1.0
car_controls.steering = 0.0
car_controls.is_manual_gear = False
car_client.setCarControls(car_controls, vehicle_name="Car1")

# —————————————————————————————————————————————
# 3. Monitor the Physics 
print("\n--- Monitoring Approach and Impact ---")
for i in range(6):
    car_state = car_client.getCarState(vehicle_name="Car1")
    drone_state = drone_client.getMultirotorState(vehicle_name="Drone1")
    
    c_pos = car_state.kinematics_estimated.position
    d_pos = drone_state.kinematics_estimated.position
    
    distance_x = abs(d_pos.x_val - c_pos.x_val)
    
    time.sleep(1)

# —————————————————————————————————————————————
# 4. Cleanup
print("\n--- Stopping and Resetting ---")
car_controls.throttle = 0.0
car_controls.brake = 1.0
car_client.setCarControls(car_controls, vehicle_name="Car1")
time.sleep(1) # Wait a moment to let the car brake

drone_client.reset()
car_client.reset()

drone_client.enableApiControl(False, vehicle_name="Drone1")
car_client.enableApiControl(False, vehicle_name="Car1")

print("Finished.")