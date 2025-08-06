import bpy
import os
import csv
import numpy as np

# Indices for parsing spreadsheet
PHASE_INDEX = 0
DURATION_INDEX = 1
START_TIME_INDEX = 2
START_FRAME_INDEX = 3
LEFT_VENTRICLE_INDEX = 4
RIGHT_VENTRICLE_INDEX = 5
LEFT_ATRIUM_INDEX = 6
RIGHT_ATRIUM_INDEX = 7
AORTA_INDEX = 8
PULMONARY_ARTERY_INDEX = 9
SUPERIOR_VENA_CAVA_INDEX = 10

# Map the names of each heart chamber/artery to their index in the spreadsheet, if available
COMPONENT_PAIRS = {
    "m":    LEFT_VENTRICLE_INDEX,       # myocardium            myocardium deforms with LV
    "lv":   LEFT_VENTRICLE_INDEX,       # left ventricle
    "rv":   RIGHT_VENTRICLE_INDEX,      # right ventricle
    "la":   LEFT_ATRIUM_INDEX,          # left atrium
    "ra":   RIGHT_ATRIUM_INDEX,         # right atrium
    "a":    AORTA_INDEX,                # aorta
    "pa":   PULMONARY_ARTERY_INDEX,     # pulmonary artery
    "svc":  SUPERIOR_VENA_CAVA_INDEX    # superior vena cava
}

# Constant names
CUSTOM_PROPERTIES_EMPTY = "HeartControl"
PROJECT_DIR_NAME = "cardiac"

# Store the results of the last data query
loaded_data = None
frame_rate = -1
frame_count = -1


def main():
    # Load data
    load_data()

    # Initialize custom properties
    get_custom_properties()

    # Insert keyframes for each frame
    insert_keyframes("frame", list(range(int(frame_count))))

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def load_data() -> bool:
    """Load the spreadsheet data in the assets folder. Returns true if the data exists, false otherwise."""
    global loaded_data, frame_count, frame_rate

    # Resolve data path
    data_path = build_path("assets/anim_data.csv")

    # Verify data path exists
    if not os.path.exists(data_path):
        print(f"Error: Could not find animation data spreadsheet at '{data_path}'")
        return False
    
    # Load data from spreadsheet at data path
    with open(data_path, newline="\n") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")

        # Read data
        read_row = False
        anim_data = []      # 2D array. First index is for row, second is for column.
        for row in reader:
            # Skip empty rows
            if not row or row[0] == "":
                read_row = False
                continue

            # Read frame_rate, frame_count
            if row[0] == "frame rate":
                frame_rate = int(row[1])
                continue

            if row[0] == "frame count":
                frame_count = int(row[1])
                continue

            # After reading "Phase", the next lines are data until an empty line is reached
            if "Phase" in row[0]:
                read_row = True
                continue

            if read_row:
                anim_data.append(row)
                continue

    # Update frame constraints for scene
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = frame_count - 1

    # Set global variable to the loaded data
    loaded_data = anim_data
    return True


def insert_keyframes(req_metric: str, req_values: list) -> bool:
    """Given a metric ('frame' or 'phase'), and a list of discrete values, insert keyframes for the animation of each component."""
    global loaded_data

    # Ensure data is loaded
    if loaded_data is None:
        print("Error: Data failed to load.")
        return False

    # Update volumes based on phase input
    if req_metric.lower().strip() == "phase":
        for phase in req_values:
            phase_row_index = int(phase) - 1   # since row 0 corresponds to phase 1, row 1 to phase 2, etc.
            for component_name in COMPONENT_PAIRS:
                if component_name.key != -1:
                    component_name = component_name.key
                    phase_frame = [int(data) for data in loaded_data[phase_row_index][START_FRAME_INDEX]] # get the starting frame corresponding to this phase
                    component_column_index = component_name.value
                    _insert_keyframe(component_name, phase_frame, [float(data) for data in loaded_data[phase_row_index][component_column_index]])
        
        return True

    # Update volumes based on frame input
    elif req_metric.lower().strip() == "frame":
        # Always interpolate frames to ensure continuity:
        for component_name in COMPONENT_PAIRS:
            # Get component column index
            component_column_index = COMPONENT_PAIRS.get(component_name)
            if component_column_index == -1:
                print(f"Warning: No data available for component '{component_name}'. Skipping.")
                continue

            # Using numpy regression, approximate a polynomial for the volume of the component at each frame
            x = np.array([float(loaded_data[row][START_FRAME_INDEX]) for row in range(len(loaded_data))])
            y = np.array([float(loaded_data[row][component_column_index]) for row in range(len(loaded_data))])
            polynomial = np.poly1d(np.polyfit(x, y, 3))

            # Update the component volume with the approximated volume at the input frame
            for frame in req_values:
                frame = int(frame)
                value = polynomial(frame)
                _insert_keyframe(component_name, frame, value)
        
        return True

    # Handle bad input
    else:
        print(f"Error: Could not recognize the input '{req_metric}'. Try 'phase' or 'frame'.")
        return False


def get_custom_properties() -> bpy.types.Object:
    """If the custom properties object is missing, create it."""
    global CUSTOM_PROPERTIES_EMPTY

    # Try to find the custom properties object
    obj = bpy.data.objects.get(CUSTOM_PROPERTIES_EMPTY)

    # If the empty properties object does not exist, initialize it
    if not obj:
        # Add the empty object
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
        obj = bpy.context.object
        obj.name = CUSTOM_PROPERTIES_EMPTY

        # Link to root scene collection and unlink from current collection if necessary
        root_collection = bpy.context.scene.collection
        if obj.name not in root_collection.objects:
            root_collection.objects.link(obj)

        # Unlink from all other collections except root
        for coll in obj.users_collection:
            if coll != root_collection:
                coll.objects.unlink(obj)

        # Initialize custom properties
        for component_name in COMPONENT_PAIRS:
            obj[component_name] = -1
    
    return obj


def _insert_keyframe(component_name: str, frame: int, value: float) -> bool:
    """Insert a keyframe for the component. This controls the volume of the component over time."""

    # Add the keyframe to the custom properties object
    custom_prop_obj = get_custom_properties()
    custom_prop_obj[component_name] = value
    custom_prop_obj.keyframe_insert(data_path=f'["{component_name}"]', frame=frame)

    # Find the component object
    obj = bpy.data.objects[component_name]
    if not obj:
        print(f"Could not find object by name '{component_name}' in scene.")
        return False
    
    # Find the bone and ensure that the driver is configured
    for modifier in obj.modifiers:
        if modifier.type == 'ARMATURE':
            armature_obj = modifier.object
            armature_data = armature_obj.data

            # Focus on armature, swap to pose mode
            bpy.context.view_layer.objects.active = armature_obj
            bpy.ops.object.mode_set(mode='POSE')

            # Get bone
            bone = list(armature_data.bones)[0].name        # we are assuming that each component has only one bone
            pose_bone = armature_obj.pose.bones[bone]

            # Get data path for scale vector
            data_path = pose_bone.path_from_id("scale")

            # Ensure the armature obj has animation data
            if not armature_obj.animation_data:
                armature_obj.animation_data_create()

            # Initialize driver if it does not exist
            _init_driver(pose_bone, data_path, component_name)


def _init_driver(pose_bone: bpy.types.PoseBone, data_path: str, component_name: str):
    # Init driver
    for i in range(3):
        d = pose_bone.id_data.driver_add(data_path, i)      # i is the index for x, y, z scale
        
        # Make first variable (Volume)
        var1 = d.driver.variables.new()
        var1.name = "volume"
        var1.targets[0].id = bpy.data.objects[CUSTOM_PROPERTIES_EMPTY]
        var1.targets[0].data_path = f'["{component_name}"]'

        # Get mean volume
        mean = _get_mean_volume(COMPONENT_PAIRS.get(component_name))

        # Set driver expression
        d.driver.expression = f"{var1.name}/{mean}"


def _get_mean_volume(component_index: int) -> float:
    values = [float(row[component_index]) for row in loaded_data]
    return sum(values) / float(len(values))


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