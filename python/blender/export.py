import bpy
import os
import init
import sys

import fixups

# Install tqdm in the python blender environment
import subprocess
subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
from tqdm import tqdm


def export_heart(rel_dir: str, filename: str, export_format: str) -> bool:
    """Handle the exporting of the heart in a UE5-compatible format."""
    # Ensure the unit scale is correct
    fixups.correct_scale()

    # Resolve output dir
    abs_dir = init.build_path(rel_dir)

    # Ensure the export path exists
    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir)

    # Handle exporting
    if "fbx c" in export_format.lower():
        # Call fbx export method
        print(f"Trying to export file to {abs_dir}/{filename}.fbx")
        success = _export_fbx_continuous(abs_dir, filename)
        return success
    elif "fbx d" in export_format.lower():
        # Call fbx export method
        print(f"Trying to export file to {abs_dir}/{filename}.fbx")
        success = _export_fbx_discontinuous(abs_dir, filename)
        return success
    elif "abc" in export_format.lower() or "alembic" in export_format.lower():
        # Call abc export method
        print(f"Trying to export file to {abs_dir}/{filename}.abc")
        success = _export_abc(abs_dir, filename)
        return success
    else:
        print(f"Error: Invalid export method declaration '{export_format}'")


def _export_fbx_continuous(abs_dir: str, filename:str) -> bool:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH', extend=True)
    bpy.ops.object.select_by_type(type='ARMATURE', extend=True)
    bpy.ops.object.select_by_type(type='EMPTY', extend=True)

    filepath = os.path.join(abs_dir, f"{filename}.fbx")
    bpy.ops.export_scene.fbx(filepath=filepath, 
                             path_mode="ABSOLUTE",
                             object_types={'ARMATURE', 'MESH'},
                             use_mesh_modifiers=False,
                             mesh_smooth_type='FACE',
                             add_leaf_bones=False,
                             bake_anim_use_nla_strips=False,
                             bake_anim_use_all_actions=False,
                             use_custom_props=True
                             )

    print(f"Successfully saved FBX file at \"{filepath}\"")
    bpy.ops.object.select_all(action='DESELECT')
    return True


def _export_fbx_discontinuous(abs_dir: str, filename:str) -> bool:
    frames = [0, 6, 9, 17, 27, 32, 38]
    # For each frame in frames...
    for frame in frames:
        # Set scene anim to frame
        bpy.context.scene.frame_current = frame

        # Update object names in scene to prevent collision when importing in UE5
        objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        for obj in objs:
            if "_" in obj.name:
                obj.name = f"{obj.name.split('_')[0]}_{frame}"
            else:
                obj.name = f"{obj.name}_{frame}"

        # Export all meshes
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH', extend=True)

        filepath = os.path.join(abs_dir, f"{filename}_frame_{frame}.fbx")
        bpy.ops.export_scene.fbx(filepath=filepath, 
                                path_mode="ABSOLUTE",
                                object_types={'MESH'},
                                use_mesh_modifiers=True,
                                mesh_smooth_type='FACE',
                                add_leaf_bones=False,
                                bake_anim=False)

        print(f"Successfully saved FBX file at \"{filepath}\"")
    bpy.ops.object.select_all(action='DESELECT')
    return True



def _export_abc(abs_dir: str, filename:str) -> bool:
    bpy.ops.object.select_all(action='DESELECT')

    # Loop: Select each mesh and its related objects, then export it
    iterable_meshes = [object for object in bpy.data.objects if object.type == 'MESH']
    for obj in tqdm(iterable_meshes):
        # Select object
        obj.select_set(True)

        # Select armature if it exists
        armature_name = obj.name.replace("SM_", "A_")
        if armature_name in bpy.data.objects:
            bpy.data.objects[armature_name].select_set(True)
        else:
            print(f"Could not find armature '{armature_name}'")

        # # Select custom parameters empty if it exists
        # if "Heart Control" in bpy.data.objects:
        #     bpy.data.objects["Heart Control"].select_set(True)
        # else:
        #     print(f"Could not find empty 'Heart Control'")

        # Export
        filepath = os.path.join(abs_dir, f"{filename}_{obj.name.strip('SK_')}.abc")
        bpy.ops.wm.alembic_export(
            filepath=filepath,
            selected=True,
            flatten=True,
            apply_subdiv=False,
            use_instancing=False,
            triangulate=True,
            quad_method='BEAUTY',
            ngon_method='BEAUTY',
            export_hair=False,
            export_particles=False,
            evaluation_mode='VIEWPORT'
        )
        
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')

        # Print
        print(f"Successfully saved Alembic file at \"{filepath}\"")
    
    print("Export complete")
    return True


if __name__ == "__main__":
    export_heart("assets/temp", "unnamed_export", "fbx discontinuous")