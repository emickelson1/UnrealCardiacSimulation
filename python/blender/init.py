import os
import sys
import bpy
import importlib


PROJECT_DIR_NAME = "cardiac"
CUSTOM_PROPERTIES_EMPTY = "HeartControl"
HEART_COMPONENTS = {
    "m",
    "lv",
    "rv",
    "la",
    "ra",
    "a",
    "pa",
    "svc"
}

def setup_paths() -> str:
    """Set up the base path for the project and add necessary directories to sys.path."""
    scripts_dir = build_path("python/blender")
    if scripts_dir not in sys.path:
        sys.path.append(scripts_dir)
    return scripts_dir


def build_path(rel_dir: str) -> str:
    """Make a path to a directory within the project structure."""
    global PROJECT_DIR_NAME

    # In case rel_dir starts or ends with a slash, remove it
    rel_dir = rel_dir.strip("/")

    # Get blend file path
    blend_path = bpy.data.filepath

    # Find parent of current directory until project root is reached
    proj_dir = os.path.dirname(blend_path)
    while (not proj_dir.endswith(PROJECT_DIR_NAME)): 
        proj_dir = os.path.dirname(proj_dir)

    # Append relative path of anim_data.csv to get data path
    data_path = os.path.join(proj_dir, rel_dir)

    return data_path


def load_and_register_scripts():
    # Order matters for dependencies
    scripts = [
        "init_weights",
        "init_armature",
        "init_anim",
        "export"
    ]

    for script_name in scripts:
        try:
            # Import fresh each time in case it's already been loaded
            if script_name in sys.modules:
                module = importlib.reload(sys.modules[script_name])
            else:
                module = importlib.import_module(script_name)

            # If the script has a register function (for bpy UI), call it
            if hasattr(module, "register"):
                module.register()
                print(f"[init_scripts] Registered: {script_name}")
            else:
                print(f"[init_scripts] Skipped {script_name} (no register())")

        except Exception as e:
            print(f"[init_scripts] Error loading {script_name}: {e}")

setup_paths()
load_and_register_scripts()
print("[init_scripts] Script initialization complete.")

if __name__ == "__main__":
    import init_weights
    import init_armature
    import init_anim   

    init_weights.main()
    print("[init_weights] Initialization complete.")

    init_armature.main()
    print("[init_armature] Initialization complete.")

    init_anim.main()
    print("[init_anim] Initialization complete.")

    init_weights.main()
    print("[init_weights] Re-initialization complete.")
