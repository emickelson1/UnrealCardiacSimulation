import bpy
import os


def export_heart(rel_dir: str, filename: str, export_method: str) -> bool:
    """Handle the exporting of the heart in a UE5-compatible format."""

    # Name of the project root dir
    project_dir_name = "cardiac"

    # Resolve output dir
    blend_path = bpy.data.filepath
    proj_dir = os.path.dirname(blend_path)
    while (not proj_dir.endswith(project_dir_name)):
        proj_dir = os.path.dirname(proj_dir)
    abs_dir = os.path.join(proj_dir, rel_dir)

    # Ensure the export path exists
    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir)

    # Handle exporting
    if export_method.lower().contains("fbx"):
        # Call fbx export method
        print(f"Trying to export file to {abs_dir}/{filename}.fbx")
        success = export_fbx(abs_dir, filename)
        return success

    if export_method.lower().contains("abc") or export_method.lower().contains("alembic"):
        # Call abc export method
        print(f"Trying to export file to {abs_dir}/{filename}.abc")
        success = export_abc(abs_dir, filename)
        return success


def export_fbx(abs_dir: str, filename:str) -> bool:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH', extend='True')
    bpy.ops.object.select_by_type(type='ARMATURE', extend='True')
    bpy.ops.object.select_by_type(type='EMPTY', extend='True')

    filepath = os.path.join(abs_dir, filename, ".fbx")
    bpy.ops.export_scene.fbx(filepath=filepath, 
                             use_selection=True, 
                             path_mode="ABSOLUTE",
                             object_types={'ARMATURE', 'MESH', 'EMPTY'},
                             use_mesh_modifiers=False,
                             mesh_smooth_type='FACE',
                             add_leaf_bones=False
                             )

    print(f"Successfully saved FBX file at \"{filepath}\"")
    bpy.ops.object.select_all(action='DESELECT')
    return True


def export_abc(abs_dir: str, filename:str) -> bool:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH', extend='True')
    bpy.ops.object.select_by_type(type='ARMATURE', extend='True')
    bpy.ops.object.select_by_type(type='EMPTY', extend='True')

    filepath = os.path.join(abs_dir, filename, ".abc")
    bpy.ops.wm.alembic_export(filepath=filepath,
                              selected=True,
                              flatten=False,
                              apply_subdiv=True,
                              use_instancing=False,
                              triangulate=True,
                              quad_method='BEAUTY',
                              ngon_method='BEAUTY',
                              export_hair=False,
                              export_particles=False,
                              )

    print(f"Successfully saved Alembic file at \"{filepath}\"")
    bpy.ops.object.select_all(action='DESELECT')
    return True