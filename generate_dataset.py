import numpy as np
import os
import argparse

def generate_dataset(output_dir, num_files=50, file_size_mb=100, seed=42):
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(seed)
    
    num_samples = 10000
    target_bytes = file_size_mb * 1024 * 1024
    label_bytes = num_samples * 8
    data_bytes = target_bytes - label_bytes
    features = max(1, data_bytes // (num_samples * 4))
    
    total_size = 0
    print(f"Generating {num_files} files of ~{file_size_mb}MB each into {output_dir}")
    
    for i in range(num_files):
        data = np.random.rand(num_samples, features).astype(np.float32)
        labels = np.random.randint(0, 2, size=(num_samples,)).astype(np.int64)
        
        data_path = os.path.join(output_dir, f"data_chunk_{i:03d}_x.npy")
        label_path = os.path.join(output_dir, f"data_chunk_{i:03d}_y.npy")
        
        np.save(data_path, data)
        np.save(label_path, labels)
        
        size = os.path.getsize(data_path) + os.path.getsize(label_path)
        total_size += size
        print(f"Written chunk {i} ({size / (1024*1024):.2f} MB)")
        
        del data, labels
    
    print(f"Generation complete. Total size: {total_size / (1024**3):.2f} GB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default="synthetic_dataset")
    parser.add_argument("--num_files", type=int, default=50)
    parser.add_argument("--file_size_mb", type=int, default=100)
    args = parser.parse_args()
    
    generate_dataset(args.output_dir, args.num_files, args.file_size_mb)
