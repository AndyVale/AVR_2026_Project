import time
import random
from cosysairsim.client import MultirotorClient, CarClient
from cosysairsim.types import CarControls

d_client = MultirotorClient(port=41451)
c_client = CarClient(port=41452)

drones =["Drone1", "Drone2", "Drone3"]
cars = ["Car1", "Car2", "Car3"]

for d in drones:
    d_client.enableApiControl(True, d)
    d_client.armDisarm(True, d)
for c in cars:
    c_client.enableApiControl(True, c)

futures =[d_client.takeoffAsync(vehicle_name=d) for d in drones]
for f in futures: f.join()

print("Initiating random chaos...")

# Run 4 cycles of random movements
for _ in range(4):
    # Randomize Cars
    for c in cars:
        ctrl = CarControls()
        ctrl.throttle = random.uniform(-1.0, 1.0)  # Random forward/reverse
        ctrl.steering = random.uniform(-1.0, 1.0)  # Random left/right
        c_client.setCarControls(ctrl, c)

    # Randomize Drones
    for d in drones:
        r_x = random.uniform(-20, 20)
        r_y = random.uniform(-20, 20)
        r_z = random.uniform(-1, -15)  # Random altitude
        r_v = random.uniform(5, 15)    # Random speed
        d_client.moveToPositionAsync(r_x, r_y, r_z, r_v, vehicle_name=d)
    
    time.sleep(2.5)

d_client.reset()
c_client.reset()