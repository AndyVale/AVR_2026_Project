import time
from cosysairsim.client import CarClient, MultirotorClient
from cosysairsim.types import CarControls

# —————————————————————————————————————————————
# Configuration
DRONE_PORT = 41451
CAR_PORT   = 41452

DRONES = ["Drone1", "Drone2"]
CARS   = ["Car1", "Car2"]

# —————————————————————————————————————————————
# Connect to the CosysAirSim API
print("Connecting to simulator...")

# Initialize Drones
drone_client = MultirotorClient(port=DRONE_PORT)
drone_client.confirmConnection()
for d in DRONES:
    drone_client.enableApiControl(True, vehicle_name=d)
    drone_client.armDisarm(arm=True, vehicle_name=d)

# Initialize Cars
car_client = CarClient(port=CAR_PORT)
car_client.confirmConnection()
for c in CARS:
    car_client.enableApiControl(True, vehicle_name=c)

car1_controls = CarControls()
car2_controls = CarControls()

# —————————————————————————————————————————————
# 1. Takeoff Fleet
print("Drones: Initiating fleet takeoff...")
f_t1 = drone_client.takeoffAsync(vehicle_name="Drone1")
f_t2 = drone_client.takeoffAsync(vehicle_name="Drone2")
f_t1.join()
f_t2.join()
print("Drones: Airborne and ready.")

# —————————————————————————————————————————————
# 2. Execute Convoy Maneuver
print("Cars: Starting convoy...")
# Car1 drives fast
car1_controls.throttle = 0.8
car1_controls.steering = 0.0
car_client.setCarControls(car1_controls, vehicle_name="Car1")

# Car2 drives slower, acting as the rear guard
car2_controls.throttle = 0.5
car2_controls.steering = 0.0
car_client.setCarControls(car2_controls, vehicle_name="Car2")

print("Drones: Starting escort patterns...")
# Drone1 scouts far ahead (X=40) at a high altitude (Z=-12) and high speed (6 m/s)
drone_client.moveToPositionAsync(40, 0, -12, 6, vehicle_name="Drone1")

# Drone2 closely escorts Car2 (X=20) at a lower altitude (Z=-4) and slower speed (3 m/s)
drone_client.moveToPositionAsync(20, 5, -4, 3, vehicle_name="Drone2")

# —————————————————————————————————————————————
# 3. Monitor the Fleet
print("\n--- Monitoring Fleet Positions ---")
for i in range(40):
    c1_pos = car_client.getCarState(vehicle_name="Car1").kinematics_estimated.position
    c2_pos = car_client.getCarState(vehicle_name="Car2").kinematics_estimated.position
    d1_pos = drone_client.getMultirotorState(vehicle_name="Drone1").kinematics_estimated.position
    d2_pos = drone_client.getMultirotorState(vehicle_name="Drone2").kinematics_estimated.position
    
    time.sleep(1)

# —————————————————————————————————————————————
# 4. Stop and Cleanup
print("\n--- Halting Fleet and Resetting ---")

# Brake both cars
car1_controls.throttle = 0.0
car1_controls.brake = 1.0
car_client.setCarControls(car1_controls, vehicle_name="Car1")

car2_controls.throttle = 0.0
car2_controls.brake = 1.0
car_client.setCarControls(car2_controls, vehicle_name="Car2")

time.sleep(1) # Let the cars brake

# Reset environment
drone_client.reset()
car_client.reset()

# Release controls
for d in DRONES:
    drone_client.enableApiControl(False, vehicle_name=d)
for c in CARS:
    car_client.enableApiControl(False, vehicle_name=c)

print("Finished.")