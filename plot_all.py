import re
import os
import matplotlib.pyplot as plt
from collections import defaultdict

DATA_DIR = "./results" 
PICTURES_DIR = "./pictures"
os.makedirs("pictures", exist_ok=True)
trace_data = defaultdict(dict)

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
    parts = config_name.split("_")
    return f"{parts[-3]}_{parts[-2]}"

def extract_config_type(config_name):
    parts = config_name.split("_")
    return "_".join(parts[1:-3])  # Extract type part (lru_no/ship_no/ship_spp_dev)

# Parse all files
for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):
        continue
    filepath = os.path.join(DATA_DIR, filename)
    try:
        config_and_trace = filename[:-4]
        config_part, trace_part = config_and_trace.rsplit(".", 1)
        trace_name = trace_part.split(".")[0]
    except ValueError:
        print(f"Skipped file: {filename}")
        continue
    hit_rate = parse_hit_rate(filepath)
    if hit_rate is not None:
        trace_data[trace_name][config_part] = hit_rate

# Combined plotting
traces = sorted(trace_data.keys())
all_x = []
all_hit_rates = []
all_colors = []
all_config_types = []
group_positions = []
current_x = 0
gap = 1

def sort_config_key(config):
    set_ways = extract_set_ways(config)
    set_size, ways = map(int, set_ways.split("_"))
    config_type = extract_config_type(config)
    type_order = CONFIG_ORDER.index(config_type)
    return (set_size, ways, type_order)

CONFIG_ORDER = ["lru_no", "ship_no", "ship_spp_dev"]

for trace_name in traces:
    config_hits = trace_data[trace_name]
    # Sort configs by set_ways
    configs = sorted(config_hits.keys(), key=lambda c: (
        int(extract_set_ways(c).split('_')[0]),
        int(extract_set_ways(c).split('_')[1])
    ))
    
    # Generate colors and config types
    set_ways_list = [extract_set_ways(c) for c in configs]
    unique_set_ways = sorted(set(set_ways_list))
    for i, sw in enumerate(unique_set_ways):
        set_ways_color[sw] = COLOR_PALETTE[i % len(COLOR_PALETTE)]
    colors = [set_ways_color[sw] for sw in set_ways_list]
    config_types = [extract_config_type(c) for c in configs]
    configs = sorted(config_hits.keys(), key=sort_config_key)
    
    # Store data
    num_bars = len(configs)
    x_positions = [current_x + i for i in range(num_bars)]
    all_x.extend(x_positions)
    all_hit_rates.extend([config_hits[c] for c in configs])
    all_colors.extend(colors)
    all_config_types.extend(config_types)
    
    # Calculate group position
    group_middle = current_x + (num_bars - 1)/2
    group_positions.append(group_middle)
    current_x += num_bars + gap

# Create figure with adjusted layout
plt.figure(figsize=(20, 10))
bars = plt.bar(all_x, all_hit_rates, color=all_colors, width=0.5)

# Add config type labels below bars (lower position)
for x, config_type in zip(all_x, all_config_types):
    plt.text(x, -0.05, config_type,         # Lowered y-position from -0.02 to -0.05
            rotation=90, ha='center', va='top', 
            fontsize=7, color='black', alpha=0.7)  # Smaller font size

# Configure axes with separated labels
ax = plt.gca()

# Set trace names (group labels) above with padding
ax.set_xticks(group_positions)
ax.set_xticklabels(traces, rotation=0)
ax.tick_params(axis='x', which='major', pad=65)  # Increased padding from 15 to 25

# Set regular x-axis labels (config types) are already handled by text

# Add horizontal line to separate labels
plt.axhline(y=0, color='black', linewidth=0.8)

# Adjust title and layout
plt.title("Hit Rate (L2C) for All Traces", pad=20)
plt.ylabel("HIT / ACCESS")
plt.ylim(0, 1)
plt.grid(True, linestyle='--', alpha=0.4)

# legend for set/ways
for sw, color in set_ways_color.items():
    plt.bar(-1, 0, color=color, label=sw)   # dummy bars for legend
plt.legend(title="Set/Ways", bbox_to_anchor=(1.05, 1), loc="upper left")


# Increase bottom margin and adjust layout
plt.subplots_adjust(bottom=0.4, top=0.9)  # More bottom space, less top space
plt.savefig(f"{PICTURES_DIR}/combined_hit_rate.png", bbox_inches='tight')
plt.close()

