import time
from cosysairsim.client import MultirotorClient

client = MultirotorClient(port=41451)
drones =["Drone1", "Drone2", "Drone3"]

for d in drones:
    client.enableApiControl(True, d)
    client.armDisarm(True, d)

futures =[client.takeoffAsync(vehicle_name=d) for d in drones]
for f in futures: f.join()

print("Executing high-speed crossing maneuver...")
# Drone1 (Left) flies Right, Drone2 (Right) flies Left, Drone3 (Center) flies Up
client.moveToPositionAsync(0, 15, -5, 12, vehicle_name="Drone1")
client.moveToPositionAsync(0, -15, -5, 12, vehicle_name="Drone2")
f3 = client.moveToPositionAsync(15, 0, -15, 12, vehicle_name="Drone3")

f3.join()
time.sleep(1)

for d in drones:
    client.reset()
    client.enableApiControl(False, d)