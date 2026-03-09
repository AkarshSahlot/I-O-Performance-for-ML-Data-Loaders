import matplotlib.pyplot as plt
import pandas as pd

def analyze():
    data = {
        "Ranks": [1, 2, 4, 8, 32],
        "Runtime (s)": [244.40, 298.64, 209.87, 215.18, 228.32],
        "Bytes Read (MiB)": [52.58, 52.58, 52.58, 52.58, 52.58],
        "I/O Perf (MiB/s)": [126.61, 242.81, 507.56, 474.52, 473.50],
        "Access Sizes": ["80,84,88,82", "84,88,78,90", "84,78,88,90", "84,88,78,90", "75,78,84,90"]
    }
    
    df = pd.DataFrame(data)
    print("Darshan Extrapolated Data Summary Table:")
    print(df.to_markdown(index=False))
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(df["Ranks"], df["Runtime (s)"], marker='o', linestyle='-', color='indigo')
    plt.title("Epoch Runtime vs MPI Ranks")
    plt.xlabel("Number of Ranks")
    plt.ylabel("Runtime (seconds)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(df["Ranks"])
    
    plt.subplot(1, 2, 2)
    plt.plot(df["Ranks"], df["I/O Perf (MiB/s)"], marker='s', linestyle='-', color='teal')
    plt.title("Aggregate I/O Perf vs Ranks")
    plt.xlabel("Number of Ranks")
    plt.ylabel("I/O Throughput (MiB/s)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(df["Ranks"])
    
    plt.tight_layout()
    plt.savefig("darshan_analysis.png", dpi=300)
    print("\nVisual charts successfully flushed to darshan_analysis.png")

if __name__ == "__main__":
    analyze()
