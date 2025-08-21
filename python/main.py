import numpy as np
import torch
import matplotlib.pyplot as plt

import loader

active_datasets = ["22x100"]
split = [1.0, 0.0, 0.0]

(train_data, train_labels), (validation_data, validation_labels), (test_data, test_labels) = loader.load_data_as_tensors(active_datasets, split)

print(f"shape: {train_labels[0].shape}")
num_unique_labels = torch.unique(train_labels[0]).numel()
unique_labels = torch.unique(train_labels[0], return_counts=True)
for i in range(num_unique_labels):
    print(f"{unique_labels[0][i]}: {unique_labels[1][i]}")


# T Z Y X


def show_2d(data: list, label: list, scan: int, frame: int, slice: int = 0):
    """
    Display a single slice from data and label side by side.

    Parameters:
        data: list of tensors or arrays [scan][time][slice, x, y]
        label: list of tensors or arrays [scan][time][slice, x, y]
        scan: index for scan
        time: index for time
        slice: index for slice
    """
    data_slice = data[scan][frame][slice].permute(1, 0)  # swap axes
    label_slice = label[scan][frame][slice].permute(1, 0)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    fig.suptitle(f"Scan {scan}, Frame {frame}, Slice {slice}")

    axes[0].imshow(data_slice, origin='lower')
    axes[0].set_title("Data Slice")
    
    axes[1].imshow(label_slice, origin='lower')
    axes[1].set_title("Label Slice")
    
    plt.show()


# Example of cycling through slices interactively
def cycle_slices(data, label, scan, time):
    slice = 0
    n_slices = len(data[scan][time])

    while True:
        command = input(f"Enter a frame number, (n)ext, (p)revious, or (q)uit: ").strip().lower()
        #Slice {slice_index+1}/{n_slices}. 
        
        if command == 'n':
            slice = (slice + 1) % n_slices
        elif command == 'p':
            slice = (slice - 1) % n_slices
        elif command == 'q':
            break
        else:
            try:
                if int(command) >= 0:
                    slice = int(command) % n_slices
            except ValueError:
                print("Invalid command.")

        show_2d(data, label, scan, time, slice)

cycle_slices(train_data, train_labels, 0, 4)