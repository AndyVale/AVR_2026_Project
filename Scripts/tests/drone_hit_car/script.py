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
drone_client.armDisarm(arm=True, vehicle_name="Drone1")

car_client = CarClient(port=CAR_PORT)
car_client.confirmConnection()
car_client.enableApiControl(True, vehicle_name="Car1")
car_controls = CarControls()

# —————————————————————————————————————————————
# 1. Setup the Scene
print("Car1: Applying brakes and sitting still as the target...")
car_controls.throttle = 0.0
car_controls.brake = 1.0
car_controls.steering = 0.0
car_controls.is_manual_gear = False
car_client.setCarControls(car_controls, vehicle_name="Car1")

print("Drone1: Taking off…")
drone_client.takeoffAsync(vehicle_name="Drone1").join()

# Wait 1 second to ensure the car has fully dropped to the floor and settled
time.sleep(1)

# —————————————————————————————————————————————
# 2. Dynamically Calculate the Hit Level
# Get the car's exact position. In NED, subtracting 0.5 moves the target 0.5m UP from the car's center.
car_pos = car_client.getCarState(vehicle_name="Car1").kinematics_estimated.position
target_z = car_pos.z_val - 0.5 

print(f"Calculated Car Z-level: {car_pos.z_val:.2f}")
print(f"Drone1: Locking altitude to Z={target_z:.2f} to hit the car chassis!")

# —————————————————————————————————————————————
# 3. Initiate the Crash (Drone)
# The car is at X=15. We tell the drone to fly to X=25 (past the car).
drone_client.moveToPositionAsync(25, 0, target_z, 8, vehicle_name="Drone1")

# —————————————————————————————————————————————
# 4. Monitor the Physics 
print("\n--- Monitoring Approach and Impact ---")
for i in range(8):
    car_state = car_client.getCarState(vehicle_name="Car1")
    drone_state = drone_client.getMultirotorState(vehicle_name="Drone1")
    
    c_pos = car_state.kinematics_estimated.position
    d_pos = drone_state.kinematics_estimated.position
    
    distance_x = abs(c_pos.x_val - d_pos.x_val)
    
    time.sleep(0.5) # Faster updates to catch the high-speed impact

# —————————————————————————————————————————————
# 5. Cleanup
print("\n--- Stopping and Resetting ---")
drone_client.reset()
car_client.reset()

drone_client.enableApiControl(False, vehicle_name="Drone1")
car_client.enableApiControl(False, vehicle_name="Car1")

print("Finished.")