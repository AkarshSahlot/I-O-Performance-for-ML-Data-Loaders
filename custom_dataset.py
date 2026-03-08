import os
import glob
import numpy as np
import torch
from torch.utils.data import Dataset

class DiskDataset(Dataset):
    def __init__(self, data_dir):
        self.x_paths = sorted(glob.glob(os.path.join(data_dir, "*_x.npy")))
        self.y_paths = sorted(glob.glob(os.path.join(data_dir, "*_y.npy")))
        
        if not self.x_paths or len(self.x_paths) != len(self.y_paths):
            raise ValueError(f"Missing or mismatched .npy files in {data_dir}")
        
        first_x = np.load(self.x_paths[0], mmap_mode='r')
        self.samples_per_file = first_x.shape[0]
        self.total_samples = len(self.x_paths) * self.samples_per_file
        
        self._current_file_idx = -1
        self._active_x = None
        self._active_y = None

    def __len__(self):
        return self.total_samples

    def __getitem__(self, idx):
        file_idx = idx // self.samples_per_file
        sample_idx = idx % self.samples_per_file
        
        if self._current_file_idx != file_idx:
            self._active_x = np.load(self.x_paths[file_idx], mmap_mode='r')
            self._active_y = np.load(self.y_paths[file_idx], mmap_mode='r')
            self._current_file_idx = file_idx
            
        x = np.array(self._active_x[sample_idx])
        y = np.array(self._active_y[sample_idx])
        
        return torch.from_numpy(x), torch.from_numpy(y)
