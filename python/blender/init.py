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
PROJECT_PATH = ""

def setup_paths() -> str:
    """Set up the base path for the project and add necessary directories to sys.path."""
    scripts_dir = build_path("python/blender")
    if scripts_dir not in sys.path:
        sys.path.append(scripts_dir)
    return scripts_dir


def build_path(rel_dir: str) -> str:
    """Make a path to a directory within the project structure."""
    global PROJECT_DIR_NAME, PROJECT_PATH

    # In case rel_dir starts or ends with a slash, remove it
    rel_dir = rel_dir.strip("/")

    # Get project path
    if PROJECT_PATH == "":
        # Attempt to get path from any loaded text file
        for text in bpy.data.texts:
            if text.filepath:
                script_path = bpy.path.abspath(text.filepath)
                PROJECT_PATH = os.path.dirname(script_path)

                while not PROJECT_PATH.endswith(PROJECT_DIR_NAME):
                    parent = os.path.dirname(PROJECT_PATH)
                    if parent == PROJECT_PATH:  # reached root
                        raise RuntimeError(f"Could not find '{PROJECT_DIR_NAME}' in any parent directory.")
                    PROJECT_PATH = parent
                break
        else:
            raise RuntimeError("Could not determine script path from bpy.data.texts.")

    print(f"[init_scripts] Project path: {PROJECT_PATH}")

    # Append relative path of anim_data.csv to get data path
    data_path = os.path.join(PROJECT_PATH, rel_dir)

    return data_path


def load_and_register_scripts():
    # Order matters for dependencies
    scripts = [
        "init_weights",
        "init_armature",
        "init_anim",
        "fixups",
        "export",
        "ui"
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
                print(f"[init_scripts] Registration skipped: {script_name} (no register())")

        except Exception as e:
            print(f"[init_scripts] Error loading {script_name}: {e}")


def get_is_initialized() -> bool:
    """Check if this script has been run before in this scene."""
    # Verify that... 

    # # CUSTOM_PROPERTIES_EMPTY exists (disabled for now for .fbx import-export)
    # if not bpy.data.objects.get(CUSTOM_PROPERTIES_EMPTY):
    #     return False
    
    # # Each mesh has an armature
    # if not len(bpy.data.meshes) == len(bpy.data.armatures):
    #     return False

    # 8 armatures in total
    if not len(bpy.data.armatures) == len(HEART_COMPONENTS):
        return False

    return True

if __name__ == "__main__":

    setup_paths()
    load_and_register_scripts()
    print("[init_scripts] Script initialization complete.")

    import init_weights
    import init_armature
    import init_anim   
    import fixups

    # Check if initialization is already needed for the existing mesh
    if not get_is_initialized():
        init_weights.main()
        print("[init_weights] Initialization complete.")

        init_armature.main()
        print("[init_armature] Initialization complete.")

        init_anim.main()
        print("[init_anim] Initialization complete.")

        fixups.add_inverse_bones()
        print("[fixups] Add inverse bones complete.")