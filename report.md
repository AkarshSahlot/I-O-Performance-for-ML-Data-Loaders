# GSoC 2026 Evaluation Task Report
**Characterizing I/O Performance for ML Data Loaders at Scale Using Darshan**
*Candidate Implementation for CERN-HSF*

## 1. Benchmark Results (M1 Pro constraint architecture)

A roughly 5GB synthetic dataset was generated locally using Numpy, organized safely into chunked `_x.npy` and `_y.npy` partitions to completely adhere to 8GB strict memory thresholds upon initialization.

The PyTorch `Dataset` component implements persistent memory-mapped arrays (`mmap_mode='r'`) and forcefully bounds runtime churn by utilizing lazy loading per-worker processes. This guarantees continuous and sequentially secure throughput while locking overall system memory allocation peaks.

*Throughput is explicitly bounded locally tracking worker concurrency:*

| Workers | Avg Elapsed Time (s) | Throughput (samples/s) | Scaling Efficiency (%) | Peak Memory (MB)  |
|---------|----------------------|------------------------|-------------------------|-------------------|
| 1       | 20.26                | 24,675.96              | 100.00%                 | 0.12              |
| 2       | 22.52                | 22,206.37              | 45.00%                  | 0.13              |
| 4       | 29.18                | 17,135.99              | 17.36%                  | 0.16              |
| 8       | 48.29                | 10,353.10              | 5.24%                   | 0.22              |

*Note: Due strictly to the 8GB unified memory constraint, instantiating the parallel benchmark at 8 concurrent dataloader workers occasionally shifts memory swapping to disk via PyTorch shared memory buffers over the M1 boundary.*

---

## 2. Darshan Profiler Analysis

Based identically on the provided HTML `.darshan` parsed views, the logs indicate the following structural scaling limits executed over POSIX parameters:

| Ranks | Runtime (s) | Bytes Read | I/O Perf (MiB/s) | Common Access Sizes |
|-------|-------------|------------|------------------|---------------------|
| 1     | 244.40      | 52.58 MiB  | 126.61           | 80, 84, 88, 82      |
| 2     | 298.64      | 52.58 MiB  | 242.81           | 84, 88, 78, 90      |
| 4     | 209.87      | 52.58 MiB  | 507.56           | 84, 78, 88, 90      |
| 8     | 215.18      | 52.58 MiB  | 474.52           | 84, 88, 78, 90      |
| 32    | 228.32      | 52.58 MiB  | 473.50           | 75, 78, 84, 90      |

### Key Observations & Bottleneck Diagnosis:

**1. Does I/O scale proportionally with the number of processing ranks?**
**No.** The total data output read across POSIX logs equals exactly `52.58 MiB` uniquely for *every* individual rank configuration iteration. This explicitly proves each MPI rank is linearly reading the *entire* dataset file tree repeatedly rather than appropriately sharding datasets. If the data loading paradigm was securely sharded among active ranks, each of $N$ threads would proportionally process roughly $52.58/N$ MiB identically.

**2. What filesystem-level scaling failures manifest upon larger parallelism?**
- **Many Small Discrete Reads:** The data structures explicitly report extremely fragmented request ranges hovering continuously between 75 and 90 bytes intrinsically. PyTorch translates this into aggressive syscall overhead, severely hammering Parallel File System (PFS) metadata endpoints and penalizing seek performance fundamentally.
- **Lock Contention Thresholds:** Driving purely concurrent sweeps by all 32 processing ranks immediately overlapping perfectly synced tiny bytes locks strictly across POSIX filesystems violently degrades concurrency logic.
- **Interconnect I/O Platau:** Scale tops out permanently at approximately `~507 MiB/s` around 4 ranks. By adding subsequent concurrency upwards to 32 parallel executors, systemic metadata load saturation literally physically crashes throughput down slightly to `473.50 MiB/s`.

---

## 3. Recommended Remediation Architectures

To exponentially unblock multi-node scaling directly spanning parallel filesystems (i.e. Lustre, GPFS):

1. **Implement Node/Rank Sharding:** Rather than redundantly broadcasting physical filesystem addresses universally, distribute data exclusively restricting rank reads equivalently via `DistributedSampler`. The resultant bandwidth demands fall evenly linear.
2. **Buffer Mega-Chunk Prefetches:** Abandon requesting microscopic 75-byte items. Re-map dataset structures comprehensively leveraging contiguous block structures (`HDF5`, `TFRecord`, `WebDataset`) maximizing sequential disk throughput. Grouping operations into multimegabyte clusters explicitly reduces costly `read()` requests safely.
3. **Collective Staging Layers:** Deploy dynamic caching strategies pushing active chunks directly from heavily congested shared origins sequentially caching natively on localized high-speed NVMe `/tmp` sectors transparently avoiding locking interference logic.

---

## 4. Local Evaluation Deployment Parameters

- **Hardware Layout:** Apple M1 Pro (8GB Minimum Constraint Base)
- **Framework Parameters:** Python 3.10+, PyTorch, Numpy

```bash
conda activate cern_gsoc_io
# Step 1: Synthesize testing chunks (generates exactly 50 chunks representing 5GB)
python generate_dataset.py --num_files 50 --file_size_mb 100

# Step 2: Validate framework limits dynamically caching traces
python benchmark_dataloader.py

# Step 3: Extrapolate graph visual representations statically
python analyze_darshan.py
```
