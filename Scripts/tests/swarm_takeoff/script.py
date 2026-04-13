from cosysairsim.client import MultirotorClient

client = MultirotorClient(port=41451)
drones =["Drone1", "Drone2", "Drone3"]

for d in drones:
    client.enableApiControl(True, d)
    client.armDisarm(True, d)

print("Swarm taking off...")
futures =[client.takeoffAsync(vehicle_name=d) for d in drones]
for f in futures: f.join()

print("Rapid ascent...")
futures =[client.moveToZAsync(-15, 8, vehicle_name=d) for d in drones]
for f in futures: f.join()

print("Landing...")
futures = [client.landAsync(vehicle_name=d) for d in drones]
for f in futures: f.join()

for d in drones:
    client.reset()
    client.enableApiControl(False, d)