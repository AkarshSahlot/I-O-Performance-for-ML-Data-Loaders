import time
import gc
import tracemalloc
import csv
import torch
from torch.utils.data import DataLoader
from custom_dataset import DiskDataset

def measure_epoch(dataloader):
    start_time = time.perf_counter()
    samples = 0
    for x, y in dataloader:
        samples += x.size(0)
    end_time = time.perf_counter()
    return end_time - start_time, samples

def benchmark():
    torch.set_num_threads(1)
    
    dataset = DiskDataset("synthetic_dataset")
    batch_size = 64
    workers_list = [1, 2, 4, 8]
    
    results = []
    
    print("Running warmup epoch...")
    loader = DataLoader(dataset, batch_size=batch_size, num_workers=1, shuffle=False)
    measure_epoch(loader)
    
    base_time = None
    
    for w in workers_list:
        print(f"\nBenchmarking num_workers={w}...")
        
        gc.collect()
        tracemalloc.start()
        
        loader = DataLoader(dataset, batch_size=batch_size, num_workers=w, shuffle=False)
        
        t1, s1 = measure_epoch(loader)
        t2, s2 = measure_epoch(loader)
        
        avg_time = (t1 + t2) / 2
        throughput = s1 / avg_time
        
        if w == 1:
            base_time = avg_time
            efficiency = 100.0
        else:
            efficiency = (base_time / (w * avg_time)) * 100.0
            
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_mb = peak_mem / (1024 * 1024)
        print(f"Workers: {w} | Avg Time: {avg_time:.2f}s | Throughput: {throughput:.2f} samples/s | Scaling Efficiency: {efficiency:.2f}%")
        print(f"Peak Memory: {peak_mb:.2f} MB")
        
        results.append({
            "workers": w,
            "avg_time_s": avg_time,
            "throughput": throughput,
            "efficiency_percent": efficiency,
            "peak_mem_mb": peak_mb
        })
        
    with open("benchmark_results.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
    print("\nBenchmark complete, results saved safely to benchmark_results.csv")

if __name__ == "__main__":
    benchmark()
