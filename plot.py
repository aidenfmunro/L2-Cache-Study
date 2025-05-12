import re
import os
import matplotlib.pyplot as plt
from collections import defaultdict

DATA_DIR = "./results" 
PICTURES_DIR = "./pictures"
os.makedirs("pictures", exist_ok=True)
# Словарь: trace_name -> {config_name: hit_rate}
trace_data = defaultdict(dict)

# Цвета по конфигурациям set_ways
COLOR_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
]
set_ways_color = {}

def extract_from_line(file):
    for line in file:
        if "cpu0->cpu0_L2C TOTAL" in line:
            return list(map(int, re.findall(r'\d+', line)))
    return None

def parse_hit_rate(filepath):
    with open(filepath, "r") as f:
        numbers = extract_from_line(f)
    if numbers is None or len(numbers) < 5:
        return None
    access, hit = numbers[3], numbers[4]
    return hit / access if access else 0

def extract_set_ways(config_name):
    # Пример: champsim_lru_no_1024_16_435 -> 1024_16
    parts = config_name.split("_")
    return f"{parts[-3]}_{parts[-2]}"  # например, "1024_16"

# Разбор всех файлов
for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(DATA_DIR, filename)

    try:
        config_and_trace = filename[:-4]
        config_part, trace_part = config_and_trace.rsplit(".", 1)
        trace_name = trace_part.split(".")[0]
    except ValueError:
        print(f"Пропущен файл: {filename}")
        continue

    hit_rate = parse_hit_rate(filepath)
    if hit_rate is not None:
        trace_data[trace_name][config_part] = hit_rate

# Построение графиков
for trace_name, config_hits in trace_data.items():
    configs = list(sorted(config_hits.keys()))
    hit_rates = [config_hits[c] for c in configs]

    # Цвета по set/ways
    set_ways_list = [extract_set_ways(c) for c in configs]
    unique_set_ways = sorted(set(set_ways_list))
    for i, sw in enumerate(unique_set_ways):
        set_ways_color[sw] = COLOR_PALETTE[i % len(COLOR_PALETTE)]
    colors = [set_ways_color[sw] for sw in set_ways_list]

    plt.figure(figsize=(12, 6))
    plt.bar(configs, hit_rates, color=colors, width=0.5)
    plt.xticks(rotation=90)
    plt.title(f"Hit Rate (L2C) for {trace_name}")
    plt.ylabel("HIT / ACCESS")
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.4)

    # Легенда
    for sw in unique_set_ways:
        plt.bar(0, 0, color=set_ways_color[sw], label=sw)
    plt.legend(title="Set/Ways")

    plt.tight_layout()
    plt.savefig(f"{PICTURES_DIR}/{trace_name}_hit_rate.png")
    plt.close()

