import re
import os
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy.stats import gmean  # для геометрического среднего

DATA_DIR = "./results"
PICTURES_DIR = "./pictures"
os.makedirs(PICTURES_DIR, exist_ok=True)

# Структура: config_type -> [all_hit_rates]
data = defaultdict(list)

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

    # Конфигурация кэша — всё, кроме champsim и set/way
    config_type = "_".join(config_parts[1:-3]).lower()

    return config_type, trace

# Разбор всех файлов
for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):
        continue
    filepath = os.path.join(DATA_DIR, filename)

    result = extract_info(filename)
    if result is None:
        print(f"Пропущен файл: {filename}")
        continue

    config_type, trace = result
    hit_rate = parse_hit_rate(filepath)
    if hit_rate is not None:
        data[config_type].append(hit_rate)

# Фильтруем нужные конфигурации
TARGET_CONFIGS = {
    'lru_no': 'LRU NO',
    'ship_no': 'SHIP NO',
    'ship_spp_dev': 'SHIP SPP DEV'
}

# Собираем геометрическое среднее по всем трассам и размерам кэша
means = []
labels = []

for config_key, config_label in TARGET_CONFIGS.items():
    values = data.get(config_key, [])
    if values:
        means.append(gmean(values))
        labels.append(config_label)
    else:
        print(f"Нет данных для конфигурации: {config_label}")

# Построение графика
plt.figure(figsize=(8, 6))
bars = plt.bar(labels, means, color=['#1f77b4', '#ff7f0e', '#2ca02c'])

# Подписываем значения на столбцах
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f"{yval:.3f}", ha='center', va='bottom')

plt.ylabel("Geometric Mean Hit Rate")
plt.title("L2C Geometric Mean Hit Rate Across All Traces and Cache Sizes")
plt.ylim(0, max(means) + 0.1 if means else 1)
plt.grid(True, linestyle='--', axis='y', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(PICTURES_DIR, "geometric_mean_all_traces_and_sizes.png"))
plt.close()
