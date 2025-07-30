import bpy
import os


# Map the names of each organ to their index in the spreadsheet, if available
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
SOURCE_ROOT_COLLECTION = "source"       # the name of the root collection in the .blend file we are taking weights from
PROJECT_DIR_NAME = "cardiac"


def main():
    # Transfer weights from the source object
    transfer_weights_from_source("blender/libraries/weighted_heart.blend")


def transfer_weights_from_source(rel_path: str) -> bool:
    """Append the weights source object from a path relative to the project root."""

    # Get source .blend file path
    source_path = build_path(rel_path)
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
    for component in HEART_COMPONENTS:
        component_collection = root_collection.children.get(component)
        component = component_collection.children.get(component)
        if component:
            # Link the object to the current scene
            bpy.context.scene.collection.children.link(component)

            # Transfer the weights to the target component
            target_object = bpy.data.objects.get(component.name.strip(".001"))
            if target_object:
                transfer_weights(source=component, target=target_object)
        else:
            print(f"Warning: Could not find component '{component}' in loaded weights source collection.")
            return False

    # Remove the source collection
    bpy.data.collections.remove(root_collection, do_unlink=True)

    return True


def transfer_weights(source: bpy.types.Object, target: bpy.types.Object) -> bool:
    """Transfer the weights from the source object to the target object."""

    # Error check
    if not source or not target:
        print("Source or target object is None.")
        return False

    # Reset selection
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

    return True


def build_path(rel_dir: str = "cardiac") -> str:
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


if __name__ == "__main__":
    main()
