import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider, Button


import python.loading.simulated_nrrd_loader as simulated_nrrd_loader

active_datasets = ["19x256"]
split = [1.0, 0.0, 0.0]
label_cmap = mcolors.ListedColormap(['black', 'red', 'orange', 'blue', 'yellow', 'green', 'pink', 'lime', 'purple'])

(train_data, train_labels), (validation_data, validation_labels), (test_data, test_labels) = simulated_nrrd_loader.load_data_as_tensors(active_datasets, split)
print(torch.equal(train_data[0][0], train_data[0][1]))

# print(f"shape: {train_labels[0].shape}")
# num_unique_labels = torch.unique(train_labels[0]).numel()
# unique_labels = torch.unique(train_labels[0], return_counts=True)
# for i in range(num_unique_labels):
#     print(f"{unique_labels[0][i]}: {unique_labels[1][i]}")


def show_slice_gui(data, label):
    # Scan, frame, slice initialization
    n_scans = len(data)
    scan_idx = 0
    n_frames = len(data[0])
    frame_idx = 0
    n_slices = len(data[0][0])
    slice_idx = 0
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    plt.subplots_adjust(bottom=0.30)  # space for 3 sliders

    # Data figure
    data_slice = data[scan_idx][frame_idx][slice_idx].permute(1, 0)
    im_data = axes[0].imshow(data_slice, origin='lower', cmap='gray')
    axes[0].set_title("Data Slice")

    # Label figure
    label_slice = label[scan_idx][frame_idx][slice_idx].permute(1, 0)
    im_label = axes[1].imshow(label_slice, origin='lower', cmap=label_cmap)
    axes[1].set_title("Label Slice")

    # Title
    fig.suptitle(f"Scan {scan_idx}, Frame {frame_idx}, Slice {slice_idx}")

    # Sliders
    scan_ax_slider = plt.axes([0.2, 0.15, 0.6, 0.03])
    scan_slider = Slider(scan_ax_slider, 'Scan', 0, n_scans - 1, valinit=scan_idx, valstep=1)
    frame_ax_slider = plt.axes([0.2, 0.10, 0.6, 0.03])
    frame_slider = Slider(frame_ax_slider, 'Frame', 0, n_frames - 1, valinit=frame_idx, valstep=1)
    slice_ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
    slice_slider = Slider(slice_ax_slider, 'Slice', 0, n_slices - 1, valinit=slice_idx, valstep=1)

    def update(val):
        # Update values
        scan_idx = int(scan_slider.val)
        frame_idx = int(frame_slider.val)
        slice_idx = int(slice_slider.val)

        # Get slices from array
        data_slice = data[scan_idx][frame_idx][slice_idx].permute(1, 0)
        label_slice = label[scan_idx][frame_idx][slice_idx].permute(1, 0)

        # Update images
        im_data.set_data(data_slice)
        im_data.set_clim(vmin=data_slice.min(), vmax=data_slice.max())  # dynamic normalization
        im_label.set_data(label_slice)
        im_label.set_clim(vmin=label_slice.min(), vmax=label_slice.max())

        fig.suptitle(f"Scan {scan_idx}, Frame {frame_idx}, Slice {slice_idx}")
        fig.canvas.draw_idle()

    scan_slider.on_changed(update)
    frame_slider.on_changed(update)
    slice_slider.on_changed(update)
    plt.show()


show_slice_gui(train_data, train_labels)
