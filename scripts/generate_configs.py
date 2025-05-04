import json
import os
from pathlib import Path

BASE_CONFIG = Path("champsim_config.json")
assert BASE_CONFIG.exists(), "Base champsim_config.json not found!"

CONFIG_DIR = Path("configs")
CONFIG_DIR.mkdir(exist_ok=True)

REPLACEMENTS = ["lru", "ship"]
PREFETCHERS = ["no", "spp_dev"]
SETS_WAYS = [
    (256, 8),   # 128 KB
    (512, 8),   # 256 KB
    (512, 16),  # 512 KB
    (1024, 8),  # 512 KB
    (1024, 16), # 1024 KB
]

with open(BASE_CONFIG) as f:
    base_config = json.load(f)

for r in REPLACEMENTS:
    for p in PREFETCHERS:
        if r == "lru" and p != "no":
            continue  # skip invalid config
        for sets, ways in SETS_WAYS:
            cfg = base_config.copy()
            cfg["L2C"]["replacement"] = r
            cfg["L2C"]["prefetcher"] = p
            cfg["L2C"]["sets"] = sets
            cfg["L2C"]["ways"] = ways

            name = f"{r}_{p}_{sets}_{ways}".replace("-", "_")
            path = CONFIG_DIR / f"{name}.json"
            with open(path, "w") as out:
                json.dump(cfg, out, indent=2)

print(f"✅ Generated {len(REPLACEMENTS) * len(PREFETCHERS) * len(SETS_WAYS)} configs in '{CONFIG_DIR}/'")

