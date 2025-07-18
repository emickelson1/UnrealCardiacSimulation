import numpy as np
import torch
import matplotlib.pyplot as plt

import loader

active_datasets = ["default"]
split = [1.0, 0.0, 0.0]

(train_data, train_labels), (validation_data, validation_labels), (test_data, test_labels) = loader.load_data_as_tensors(active_datasets, split)

print(train_data)