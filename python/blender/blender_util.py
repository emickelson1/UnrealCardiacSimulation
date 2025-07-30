import bpy
import os

# Name of the project root dir
PROJECT_DIR_NAME = "cardiac"


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