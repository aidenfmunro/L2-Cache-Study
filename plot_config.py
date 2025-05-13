import re
import os
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

DATA_DIR = "./results"
PICTURES_DIR = "./pictures"
os.makedirs(PICTURES_DIR, exist_ok=True)

# Структура: config_type -> setways -> trace -> hit_rate
data = defaultdict(lambda: defaultdict(dict))

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

def extract_info(filename):
    if not filename.endswith(".txt"):
        return None

    name = filename[:-4]  # убрать .txt
    try:
        config_part, trace = name.rsplit(".", 1)
    except ValueError:
        return None  # если нет точки — пропустить

    config_parts = config_part.split("_")
    if len(config_parts) < 3:
        return None

    # Последние две части — set и way
    set_val = config_parts[-3]
    way_val = config_parts[-2]
    setways = f"{set_val}x{way_val}"

    # Конфигурация кэша — всё, кроме champsim и set/way
    config_type = "_".join(config_parts[1:-3])

    return config_type.lower(), setways, trace

# Разбор всех файлов
for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):
        continue
    filepath = os.path.join(DATA_DIR, filename)

    result = extract_info(filename)
    if result is None:
        print(f"Пропущен файл: {filename}")
        continue

    config_type, setways, trace = result
    hit_rate = parse_hit_rate(filepath)
    if hit_rate is not None:
        data[config_type][setways][trace] = hit_rate

# Построение графиков по каждой политике
for config_type, setways_data in data.items():
    setways_sorted = sorted(setways_data.keys(), key=lambda x: tuple(map(int, x.split("x"))))

    traces = sorted({trace for v in setways_data.values() for trace in v})

    x = np.arange(len(setways_sorted))  # позиции на оси X
    bar_width = 0.2

    plt.figure(figsize=(12, 6))
    for i, trace in enumerate(traces):
        values = [setways_data[sw].get(trace, 0) for sw in setways_sorted]
        plt.bar(x + i * bar_width, values, width=bar_width, label=trace)

    plt.xticks(x + bar_width, setways_sorted)
    plt.ylabel("Hit Rate")
    plt.title(f"L2C Performance: {config_type}")
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Trace")

    plt.tight_layout()
    plt.savefig(f"{PICTURES_DIR}/{config_type}_hit_rate_grouped.png")
    plt.close()

