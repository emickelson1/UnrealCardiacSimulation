import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider, Button


import loader

active_datasets = ["test-1x10"]
split = [1.0, 0.0, 0.0]
label_cmap = mcolors.ListedColormap(['black', 'red', 'orange', 'blue', 'yellow', 'green', 'pink', 'lime', 'purple'])


(train_data, train_labels), (validation_data, validation_labels), (test_data, test_labels) = loader.load_data_as_tensors(active_datasets, split)

print(f"shape: {train_labels[0].shape}")
num_unique_labels = torch.unique(train_labels[0]).numel()
unique_labels = torch.unique(train_labels[0], return_counts=True)
for i in range(num_unique_labels):
    print(f"{unique_labels[0][i]}: {unique_labels[1][i]}")


def show_slice_gui(data, label, scan, time):
    n_slices = len(data[scan][time])
    slice_idx = 0

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    plt.subplots_adjust(bottom=0.2)  # space for slider

    # Data figure
    data_slice = data[scan][time][slice_idx].permute(1, 0)
    im_data = axes[0].imshow(data_slice, origin='lower', cmap='gray')
    axes[0].set_title("Data Slice")

    # Label figure
    label_slice = label[scan][time][slice_idx].permute(1, 0)
    im_label = axes[1].imshow(label_slice, origin='lower', cmap=label_cmap)
    axes[1].set_title("Label Slice")

    # Title
    fig.suptitle(f"Scan {scan}, Frame {time}, Slice {slice_idx}")

    # Slider axis
    ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
    slider = Slider(ax_slider, 'Slice', 0, n_slices - 1, valinit=slice_idx, valstep=1)

    def update(val):
        slice_idx = int(slider.val)
        data_slice = data[scan][time][slice_idx].permute(1, 0)
        label_slice = label[scan][time][slice_idx].permute(1, 0)

        # Update images
        im_data.set_data(data_slice)
        im_data.set_clim(vmin=data_slice.min(), vmax=data_slice.max())  # dynamic normalization
        im_label.set_data(label_slice)
        im_label.set_clim(vmin=label_slice.min(), vmax=label_slice.max())

        fig.suptitle(f"Scan {scan}, Frame {time}, Slice {slice_idx}")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()


show_slice_gui(train_data, train_labels, scan=0, time=4)
