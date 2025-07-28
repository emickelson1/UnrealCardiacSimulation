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

# Map the names of each organ to their index in the spreadsheet, if available
ORGAN_PAIRS = {
    "m":    LEFT_VENTRICLE_INDEX,   # myocardium            myocardium deforms with LV
    "lv":   LEFT_VENTRICLE_INDEX,   # left ventricle
    "rv":   RIGHT_VENTRICLE_INDEX,  # right ventricle
    "la":   LEFT_ATRIUM_INDEX,      # left atrium
    "ra":   RIGHT_ATRIUM_INDEX,     # right atrium
    "svc":  -1,                     # superior vena cava    use -1 as temp value
    "pa":   -1,                     # pulmonary artery      use -1 as temp value
    "a":    -1                      # aorta                 use -1 as temp value
}

# Store the result of the last data query
loaded_data = None


def main():
    # Load data
    load_data()

    # Run the update script for frame 0
    update_organ_volumes("frame", 0)


def load_data() -> bool:
    """Load the spreadsheet data in the assets folder. Returns true if the data exists, false otherwise."""
    global loaded_data

    # Get blend file path
    blend_path = bpy.data.filepath

    # Find parent of current directory until project root is reached
    proj_dir = os.path.dirname(blend_path)
    while (not proj_dir.endswith("cardiac")): 
        proj_dir = os.path.dirname(proj_dir)

    # Append relative path of anim_data.csv to get data path
    data_path = os.join(proj_dir, "/assets/anim_data.csv")

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
            if not row or row[0] is "":
                read_row = False
                continue
            if "Phase" in row[0]:
                read_row = True
                continue
            if read_row:
                anim_data.append(row)

    # Set global variable to the loaded data
    loaded_data = anim_data
    return True


def update_organ_volumes(req_metric: str, req_value):
    """Get the volume for all organs at a specific phase, time, or frame."""
    global loaded_data

    # Update volumes based on phase input
    if req_metric.lower().strip() == "phase":
        phase = int(req_value)
        phase_row_index = phase - 1   # since row 0 corresponds to phase 1, row 1 to phase 2, etc.
        for organ in ORGAN_PAIRS:
            if organ.key is not -1:
                organ_name = organ.key
                organ_column_index = organ.value
                _update_organ_volume(organ_name, loaded_data[phase_row_index][organ_column_index])
        
        return True

    # Update volumes based on frame input
    elif req_metric.lower().strip() == "frame":
        frame = float(req_value)
        
        # Always interpolate frames to ensure continuity:
        for organ in ORGAN_PAIRS:
            if organ.key is not -1:
                organ_name = organ.key
                organ_column_index = organ.value

                # Using numpy regression, approximate a polynomial for the volume of the organ at each frame
                x = np.array(loaded_data[:, START_FRAME_INDEX])
                y = np.array(loaded_data[:, organ_column_index])
                polynomial = np.poly1d(np.polyfit(x, y, 3))

                # Update the organ volume with the approximated volume at the input frame 
                value = polynomial(frame)
                _update_organ_volume(organ_name, value)
        
        return True

    # Handle errors
    else:
        print(f"Error: Could not recognize the input '{req_metric}'. Try 'phase' or 'frame'.")
        return False


def _update_organ_volume(organ: str, value: float):
    """Update the volume of the organ given by the argument."""
    # Find the organ object 


if __name__ == "__main__":
    main()