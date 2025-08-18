import numpy as np
import torch
import matplotlib.pyplot as plt

import loader

active_datasets = ["default"]
split = [1.0, 0.0, 0.0]

(train_data, train_labels), (validation_data, validation_labels), (test_data, test_labels) = loader.load_data_as_tensors(active_datasets, split)

print(f"shape: {train_labels[0].shape}")
num_unique_labels = torch.unique(train_labels[0]).numel()
unique_labels = torch.unique(train_labels[0], return_counts=True)
for i in range(num_unique_labels):
    print(f"{unique_labels[0][i]}: {unique_labels[1][i]}")