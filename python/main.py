import torch
import numpy as np
import nrrd
import loader

active_datasets = ["default"]
data = loader.load_nrrds(active_datasets)
print(data)