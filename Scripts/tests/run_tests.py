import os
import shutil
import time
import subprocess
import argparse
from pathlib import Path
from cosysairsim.client import VehicleClient

def reload_scene():
    print("[TEST] Triggering level restart to apply new settings...")
    try:
        client = VehicleClient()
        client.confirmConnection()
        client.simRunConsoleCommand("RestartLevel")
        # Wait for Unreal to reload assets and re-initialize the C++ SimMode
        time.sleep(10) 
        print("[TEST] Scene reloaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to trigger map reload: {e}")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument("--ue5", required=True, help="Path to UnrealEditor.exe")
    parser.add_argument("--project", required=True, help="Path to .uproject")
    parser.add_argument("--tests", nargs='+', required=True, help="Folder names or 'all'")
    args = parser.parse_args()

    airsim_path = Path.home() / "Documents" / "AirSim" / "settings.json"
    airsim_path.parent.mkdir(parents=True, exist_ok=True)

    if "all" in args.tests:
        test_list = [d.name for d in Path(".").iterdir() if d.is_dir() and (d / "script.py").exists()]
    else:
        test_list = args.tests

    if not test_list:
        print("[ERROR] No valid test folders found.")
        return

    print(f"[TEST] Found {len(test_list)} tests to execute: {', '.join(test_list)}")

    # Initialize the first test settings before boot
    first_test = test_list[0]
    print(f"[TEST] Copying initial settings for '{first_test}'...")
    shutil.copy(Path(first_test) / "settings.json", airsim_path)

    print("[TEST] Starting UE5 scene (this may take a moment)...")
    ue5_proc = subprocess.Popen([
        args.ue5, args.project, "-game", "-windowed", "-ResX=1280", "-ResY=720"
    ])
    time.sleep(20) # Buffer for initial engine heavy load

    for i, name in enumerate(test_list):
        test_dir = Path(name)
        
        # If not the first test, swap settings and reload
        if i > 0:
            print(f"[TEST] Switching settings to '{name}'...")
            shutil.copy(test_dir / "settings.json", airsim_path)
            reload_scene()

        print(f"[TEST] Starting test: '{name}'")
        script_path = test_dir / "script.py"
        
        # Execute the python test script
        result = subprocess.run(["python", str(script_path)])
        
        if result.returncode == 0:
            print(f"[TEST] Test '{name}' completed successfully.")
        else:
            print(f"[ERROR] Test '{name}' failed with return code {result.returncode}")
        
        time.sleep(2)

    print("[TEST] All scheduled tests finished. Terminating UE5 process.")
    ue5_proc.terminate()
    ue5_proc.wait()
    print("[TEST] Cleanup complete. Goodbye.")

if __name__ == "__main__":
    main()