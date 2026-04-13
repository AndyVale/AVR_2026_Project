import time
from cosysairsim.client import CarClient
from cosysairsim.types import CarControls

client = CarClient(port=41452)
cars =["Car1", "Car2", "Car3"]

for c in cars:
    client.enableApiControl(True, c)

controls = CarControls()
controls.throttle = 1.0

print("Accelerating all cars to intersection...")
for c in cars:
    client.setCarControls(controls, c)

time.sleep(4)

for c in cars:
    client.reset()
    client.enableApiControl(False, c)