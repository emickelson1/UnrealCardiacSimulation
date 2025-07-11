import torch
import numpy as np
import nrrd

dir = "python/dump/"

data = np.zeros((1, 2, 3, 4))
filename = "test1_vol.nrrd"
filepath = dir + filename

# write
# nrrd.write(filepath, data)

readdata, header = nrrd.read(filepath)
print(readdata.shape)
print(header)

print(set(readdata.flatten()))