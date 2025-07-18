import nrrd
import glob
from pathlib import Path
import os

class DatasetError(Exception):
    pass

def load_nrrds(included_datasets, val_frac=.2, test_frac=.2):
    # Raise exception if no datasets are provided.
    if len(included_datasets) == 0:
        raise DatasetError("No datasets provided")
    
    # Get directory that contains datasets by default
    unprocessed_data_dir = f"{Path("./main.py").parent.absolute()}/data/unprocessed"
    
    # Load all nrrd files in the given datasets
    paths = []
    for dataset in included_datasets:
        if not os.path.isdir(f"{unprocessed_data_dir}/{dataset}"):
            raise DatasetError(f"Could not find dataset: \"{dataset}\"")
        paths.extend(glob.glob(f"{unprocessed_data_dir}/{dataset}/*_vol.nrrd"))
    data = [(nrrd.read(path)[0], nrrd.read(path.replace("_vol", "_seg"))[0]) for path in paths]
    
    # Return the data as tuples (volumes, segmentations)
    return data


