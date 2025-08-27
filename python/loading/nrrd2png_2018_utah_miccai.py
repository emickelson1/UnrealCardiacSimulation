import glob
from pathlib import Path
import numpy as np
import os
import simulated_nrrd_loader
from PIL import Image
from tqdm import tqdm
import nrrd

dataset_name = "2018_UTAH_MICCAI"

dataset_dir = f"{Path('./').parent.absolute()}/data/downloaded/{dataset_name}"
out_dir = f"{Path('./').parent.absolute()}/data/png"

def main():
    # Check if dataset_dir exists
    if not os.path.exists(dataset_dir):
        print(f"The dataset could not be found at {dataset_dir}")
        return
    
    # Load data inside dataset
    data_paths = glob.glob(f"{dataset_dir}/*/*/lgemri.nrrd")

    # Make out directory if it doesn't exist
    os.makedirs(os.path.join(out_dir, dataset_name), exist_ok=True)

    # Convert and save each nrrd as png
    for i in tqdm(range(len(data_paths))):
        arr, _ = nrrd.read(data_paths[i])
        arr = np.transpose(arr, [2, 1, 0])
        for slice_i in range(len(arr)):
            slice = arr[slice_i]
            img = Image.fromarray(slice)
            img.save(os.path.join(out_dir, dataset_name, f"nrrd_{i}_slice_{slice_i}.png"))


if __name__ == "__main__":
    main()