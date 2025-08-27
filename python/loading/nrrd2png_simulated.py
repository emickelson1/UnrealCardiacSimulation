import glob
from pathlib import Path
import numpy as np
import os
import simulated_nrrd_loader
from PIL import Image
from tqdm import tqdm


in_dir = f"{Path('./').parent.absolute()}/data/unprocessed"
out_dir = f"{Path('./').parent.absolute()}/data/png"
dataset = "19x256"

def main():
    print(f"Splitting nrrds (from '{in_dir}/{dataset}') into pngs (to '{out_dir}')")
    vol_paths = glob.glob(f"{in_dir}/{dataset}/*_vol.nrrd")

    for i in tqdm(range(len(vol_paths))):
        vol_path = vol_paths[i]
        seg_path = vol_paths[i].replace("_vol.nrrd", "_seg.nrrd")

        def save(nrrd_path: str, type: str):
            # Get name
            name = nrrd_path.lstrip(in_dir).lstrip(f"/{dataset}/").rstrip(f"_{type}.nrrd")

            # Form array
            arr = simulated_nrrd_loader.load_file_as_np(nrrd_path)
            arr = np.transpose(arr, [3, 2, 0, 1])   # frame, slice, x, y
            arr = arr[:, :, ::-1, :]                # fix flipped y
            
            # Normalize data
            if type == "vol":
                min_vals = arr.min(axis=(-2,-1), keepdims=True)
                max_vals = arr.max(axis=(-2,-1), keepdims=True)
                with np.errstate(divide='ignore'):
                    scale = np.where(max_vals > min_vals, 255 / (max_vals - min_vals), 0)
                    arr = ((arr - min_vals) * scale).astype(np.uint8)

            # Ensure out directory is valid
            out_dir = os.path.join(out_dir, dataset, type)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)

            # Iterate through frames
            for frame_i in range(len(arr)):
                for slice_i in range(int(len(arr[0]))):
                    # Resolve path
                    out_path = os.path.join(out_dir, f"{name}_frame_{frame_i}_slice_{slice_i}.png")

                    # Save slice to that path
                    slice = arr[frame_i][slice_i]
                    img = Image.fromarray(slice)
                    img.save(out_path)

        save(vol_path, 'vol')
        save(seg_path, 'seg')

if __name__ == "__main__":
    main()
