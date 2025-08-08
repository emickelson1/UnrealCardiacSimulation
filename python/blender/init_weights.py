import bpy
import os

import init

SOURCE_ROOT_COLLECTION = "source"       # the name of the root collection in the .blend file we are taking weights from


def main():
    # Center geometry on the scene origin
    center_geometry()

    # Transfer weights from the source object
    transfer_weights_from_source("blender/libraries/weighted_heart.blend")


def transfer_weights_from_source(rel_path: str) -> bool:
    """Append the weights source object from a path relative to the project root."""
    global SOURCE_ROOT_COLLECTION

    # Get source .blend file path
    source_path = init.build_path(rel_path)
    if not source_path:
        return False

    # Load the main collection in the source .blend
    with bpy.data.libraries.load(source_path) as (data_from, data_to):
        data_to.collections.append(SOURCE_ROOT_COLLECTION)
    
    # Link the collection to the current scene
    root_collection = bpy.data.collections.get(SOURCE_ROOT_COLLECTION)
    if root_collection:
        bpy.context.scene.collection.children.link(root_collection)

    # Loop through component collections
    obj_names = [f"{component}.001" for component in init.HEART_COMPONENTS]
    if len(obj_names) == 0:
        print("Warning: No components found in the source collection.")
        return False
    for obj_name in obj_names:
        # # Link the object to the current scene
        # bpy.context.scene.collection.children.link(obj)

        # Transfer the weights to the target component
        obj = bpy.data.objects.get(obj_name)
        target_obj = bpy.data.objects.get(obj_name.strip(".001"))
        if target_obj:
            transfer_weights(source=obj, target=target_obj)
        else:
            print(f"Warning: Target object '{obj_name.strip('.001')}' not found in the scene.")
    
    # Remove the source collection and objects in it
    delete_hierarchy(SOURCE_ROOT_COLLECTION)

    # for obj in list(root_collection.objects):
    #     bpy.data.objects.remove(obj, do_unlink=True)
    # bpy.data.collections.remove(root_collection, do_unlink=True)

    return True


def transfer_weights(source: bpy.types.Object, target: bpy.types.Object) -> bool:
    """Transfer the weights from the source object to the target object."""

    # Error check
    if not source or not target:
        print("Source or target object is None.")
        return False

    # Reset selection
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    # Select source
    source.select_set(True)

    # Select target and make active
    target.select_set(True)
    bpy.context.view_layer.objects.active = target

    # Transfer weights
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.data_transfer(
        use_reverse_transfer=True,     # select source first
        data_type='VGROUP_WEIGHTS',
        layers_select_src='ACTIVE',
        layers_select_dst='ACTIVE',
        mix_mode='REPLACE'
    )

    # Rename vertex group
    target.vertex_groups[-1].name=f"{target.name}_bone"

    return True


def center_geometry():
    """Center geometry on the scene origin"""

    # Deselect all meshes in the scene
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]  # select anything to set active to prevent context error on next line
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')

    # Get selected objects
    selected = [obj for obj in bpy.context.selected_objects]

    # Unlock location for all selected objects
    for obj in selected:
        obj.lock_location = (False, False, False)

    # Set each object's origin to its center of volume
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME') 

    # Set 3D cursor to the origin
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    # Get screen context override to prevent poll error
    area = [area for area in bpy.context.window.screen.areas if area.type == 'VIEW_3D'][0]
    region = [region for region in area.regions if region.type == 'WINDOW'][0]
    space = area.spaces.active
    override = {
        "window": bpy.context.window,
        "screen": bpy.context.screen,
        "area": area,
        "region": region,
        "space_data": space
        }

    # Snap selected objects to the cursor location
    with bpy.context.temp_override(**override):
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)

    # Deselect all objects in the scene
    bpy.ops.object.select_all(action='DESELECT')


def delete_hierarchy(root_coll):
    """Delete the hierarchy of objects under the parent object name."""

    # Deselect all objects
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    # Get the collection by name
    collection = bpy.data.collections.get(root_coll)
    if not collection:
        print(f"Collection '{root_coll}' not found.")
        return

    # Gather all objects in the collection (including children recursively)
    def gather_objects(coll, obj_set):
        for obj in coll.objects:
            obj_set.add(obj)
        for child_coll in coll.children:
            gather_objects(child_coll, obj_set)

    objects_to_delete = set()
    gather_objects(collection, objects_to_delete)

    # Remove animation data and select for deletion
    for obj in objects_to_delete:
        obj.animation_data_clear()
        obj.select_set(True)

    # Remove objects from the scene and data
    bpy.ops.object.delete()

    # Remove the collection itself
    bpy.data.collections.remove(collection)


if __name__ == "__main__":
    main()
