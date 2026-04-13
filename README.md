# Extending CoSys-AirSim for Multi-Domain Vehicle Simulation

This project was developed by Group G4 for the "Augmented and Virtual Reality" course at the University of Genoa (DIBRIS) during the 2025/2026 academic year.

The goal of this project is to extend the [CoSys-AirSim](https://cosys-lab.github.io/Cosys-AirSim/) framework to support multi-domain operations. Specifically, our implementation enables the simultaneous simulation of both Unmanned Aerial Vehicles (UAVs) and Unmanned Ground Vehicles (UGVs) within a single Unreal Engine 5 environment.

## Group
The members of Group G4 are as follows (in alphabetical order):
* **Ricotti Andrea Valentino**
* **Signoretti Walter**
* **Suffia Azzurra**

---

## Repository Structure

The repository is organized into the following main directories:

*   **`Airsim/`**: Contains the source code for our extension of the CoSys-AirSim plugin.
*   **`Report/`**: Contains the full project documentation, including the LaTeX source code and the final PDF version of the report.
*   **`Scripts/tests/`**: Contains the testing environment, specifically:
    *   An automation tool (`run_tests.py`) to execute multiple scenarios sequentially.
    *   Subfolders for each test, each containing a specific `settings.json` and `script.py` for targeted testing.
