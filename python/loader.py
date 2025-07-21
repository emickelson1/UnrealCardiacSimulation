import nrrd
import glob
from pathlib import Path
import os
import random
import numpy as np
import torch


class DatasetError(Exception):
    pass


def load_data_as_np(active_datasets) -> list[tuple]:
    # Raise exception if no datasets are provided.
    if len(active_datasets) == 0:
        raise DatasetError("No datasets provided")
    
    # Get directory that contains datasets by default
    unprocessed_data_dir = f"{Path("./main.py").parent.absolute()}/data/unprocessed"
    
    # Load all nrrd files in the given datasets
    paths = []
    for dataset in active_datasets:
        if not os.path.isdir(f"{unprocessed_data_dir}/{dataset}"):
            raise DatasetError(f"Could not find dataset: \"{dataset}\"")
        paths.extend(glob.glob(f"{unprocessed_data_dir}/{dataset}/*_vol.nrrd"))

    data = [(nrrd.read(path)[0], nrrd.read(path.replace("_vol", "_seg"))[0]) for path in paths]
    
    # Shuffle tuples
    random.shuffle(data)

    # Return the data as tuples (volumes, segmentations)
    return data


def load_data_as_tensors(active_datasets, 
                         split=[1.0, 0.0, 0.0],    # train, validation, test
                         reorder=(3, 2, 1, 0)):
    # Load nrrd files
    data = load_data_as_np(active_datasets)
    volumes, labels = [data_i[0] for data_i in data], [data_i[1] for data_i in data]

    # Permute data and convert to tensor
    volumes = [torch.tensor(volume).permute(reorder) for volume in volumes]
    labels = [torch.tensor(label).permute(reorder) for label in labels]

    # Split into train, validation, test
    train_start = 0
    val_start = int(len(volumes) * split[0])
    test_start = int(len(volumes) * (1 - split[2]))

    train_data = (volumes[train_start : val_start], labels[train_start : val_start])
    validation_data = (volumes[val_start : test_start], labels[val_start : test_start])
    test_data = (volumes[test_start : -1], labels[test_start : -1])

    # Return data
    return train_data, validation_data, test_data