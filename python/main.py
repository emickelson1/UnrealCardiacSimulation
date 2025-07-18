import torch
import numpy as np
import nrrd
import glob
from pathlib import Path

unprocessed_data_dir = f"{Path("./main.py").parent.absolute()}/data/unprocessed"
dataset_name = input("Enter the dataset name: ")
dataset_name = dataset_name if len(dataset_name) > 0 else "default"
seg_paths = glob.glob(f"{unprocessed_data_dir}/{dataset_name}/*_seg.nrrd")
vol_paths = [path.replace("_seg.nrrd", "_vol.nrrd") for path in seg_paths]

for i in range(0, len(seg_paths)):
    print(f"seg: {seg_paths[i]}\nvol: {vol_paths[i]}\n")

seg_data = [nrrd.read(path)[0] for path in seg_paths]
vol_data = [nrrd.read(path)[0] for path in vol_paths]

# for data in seg_data:
#     print(data.shape)

# readdata, header = nrrd.read(seg_paths[0])
# print(set(readdata.flatten()))

# print(readdata.shape)
# print(header)

print(set(seg_data[0].flatten()))