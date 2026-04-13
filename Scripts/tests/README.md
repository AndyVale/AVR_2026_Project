# Cosys-AirSim-Extension Tests

This directory contains various test scenarios to validate the multi-agent behavior of the Cosys-AirSim-Extension project. Each test has its own directory containing a `settings.json` (which configures the environment and the agents) and a `script.py` (which controls the agents using the AirSim API).

## How to use `run_tests.py`

The `run_tests.py` script is a utility wrapper that automates the testing process. It correctly places the `settings.json` file where AirSim expects it, launches the Unreal Engine 5 project automatically, and runs the python tests one after the other. It will seamlessly restart the level between tests to apply the new settings.

### Arguments

* `--ue5`: The absolute path to your `UnrealEditor.exe` executable.
* `--project`: The absolute path to your `.uproject` file.
* `--tests`: The explicit folder names of the tests you want to execute separated by spaces, or simply `all` to run every test in the folder.

### Examples

**Note:** You will need to adjust the paths to `UnrealEditor.exe` and your `.uproject` file based on your local machine setup.

#### Run all tests automatically:
```bash
python run_tests.py --ue5 "Path\To\UnrealEditor.exe" --project "Path\To\Your\Project.uproject" --tests all
```

#### Run a single test (e.g. `multi_agent_drone_car`):
```bash
python run_tests.py --ue5 "Path\To\UnrealEditor.exe" --project "Path\To\Your\Project.uproject" --tests multi_agent_drone_car
```

#### Run a specific batch of tests:
```bash
python run_tests.py --ue5 "Path\To\UnrealEditor.exe" --project "Path\To\Your\Project.uproject" --tests car_hit_drone cars_intersection_carsh swarm_takeoff
```
