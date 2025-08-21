# Multi‑Sensor Fusion for Vehicle Distance Estimation (ASYX HiRes 2019)

A reproducible, modular pipeline that estimates distances to road vehicles by combining **camera detections (YOLOv8)** with **LiDAR** and **RADAR** point clouds. The project targets the **ASYX HiRes 2019** dataset and includes dataset preparation, detection caching, 3D→2D projection, bounding‑box filtering, weighted sensor fusion, and MAE/RMSE evaluation.

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Repository Structure](#repository-structure)
- [Dataset: ASYX HiRes 2019](#dataset-asyx-hires-2019)
  - [On‑Disk Layout](#on-disk-layout)
  - [Calibration Files](#calibration-files)
  - [Ground Truth Format](#ground-truth-format)
  - [Naming Rules](#naming-rules)
  - [Build Manifests and Splits](#build-manifests-and-splits)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quickstart](#quickstart)
- [End‑to‑End Pipeline](#end-to-end-pipeline)
  - [1) Vehicle Detection (YOLOv8)](#1-vehicle-detection-yolov8)
  - [2) 3D→2D Projection](#2-3d2d-projection)
  - [3) Filter Points Inside Bounding Boxes](#3-filter-points-inside-bounding-boxes)
  - [4) Per‑Box Distance Estimation](#4-per-box-distance-estimation)
  - [5) Weighted Sensor Fusion](#5-weighted-sensor-fusion)
  - [6) Accuracy Evaluation (MAE/RMSE)](#6-accuracy-evaluation-maermse)
- [Results and Reproducibility](#results-and-reproducibility)
- [Notebooks](#notebooks)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)

---

## Overview

This repository implements a practical multi‑sensor fusion workflow to estimate distances to vehicles in camera images by fusing LiDAR and RADAR information. It uses a manifest‑first approach for the **ASYX HiRes 2019** dataset, ensuring clean separation of raw data, intermediate artifacts, and reproducible experiment results.

Core ideas:
- Run object detection on RGB images using YOLOv8 and cache labels.
- Transform LiDAR and RADAR points into the camera frame and project onto the image plane using calibration.
- For each detected vehicle bounding box, select only projected points inside the box.
- Compute a robust per‑box distance (median) for each sensor and fuse with a weighted average.
- Compare fused distances to ground truth using MAE and RMSE.

The codebase is designed for clarity, reproducibility, and extension to other datasets or fusion strategies.

---

## Key Features

- **Dataset aware:** Explicit support for **ASYX HiRes 2019** with manifest and splits.
- **Reproducible detections:** YOLOv8 results cached as YOLO‑TXT files to avoid repeated inference.
- **Modular:** Clean separation of detection, projection, filtering, fusion, and evaluation.
- **Robust distance estimate:** Uses the **median** over points in a bbox to resist outliers.
- **Fusion:** Simple, transparent weighted average (LiDAR‑heavy by default) you can tune.
- **Metrics:** MAE/RMSE against ground truth depth with handling for count mismatches.

---

## Repository Structure

```
multi-sensor-fusion-distance/
├─ README.md
├─ LICENSE
├─ requirements.txt
├─ .gitignore
├─ pyproject.toml                 # optional formatting/lint settings
├─ src/
│  └─ msf_distance/
│     ├─ __init__.py
│     ├─ detection.py             # YOLOv8 detection + label cache
│     ├─ projection.py            # LiDAR/RADAR -> camera frame projection
│     ├─ filtering.py             # bbox point-inclusion, outlier-robust summaries
│     ├─ fusion.py                # weighted fusion logic
│     ├─ evaluation.py            # MAE/RMSE and helpers
│     ├─ dataset.py               # ASYX loader, manifest utilities
│     └─ cli.py                   # end-to-end entrypoint
├─ scripts/
│  ├─ prepare_asyx.py             # scan raw data, write manifest and split.json
│  └─ run_pipeline.py             # convenience wrapper around CLI
├─ notebooks/
│  └─ 01_exploration.ipynb        # analysis / sanity checks
├─ configs/
│  ├─ asyx_hires_2019.yaml        # dataset + pipeline configuration
│  └─ yolov8.yaml                 # detector-specific parameters
├─ docs/
│  ├─ Sensor_fusion-3.pdf         # project report
│  └─ figures/                    # sample outputs for README
├─ data/
│  └─ asyx_hires_2019/
│     ├─ raw/                     # dataset (not tracked by git)
│     │  ├─ images/
│     │  ├─ lidar/
│     │  ├─ radar/
│     │  ├─ calib/
│     │  └─ gt/
│     ├─ interim/                 # manifest.csv, split.json
│     └─ processed/               # small preprocessed artifacts
├─ models/                        # weights/checkpoints (gitignored)
├─ runs/                          # detection caches, logs (gitignored)
└─ .github/
   └─ workflows/
      └─ ci.yml                   # optional CI (lint/tests)
```

The `.gitignore` is configured to exclude `data/`, `models/`, `runs/`, and other heavy or local artifacts.

---

## Dataset: ASYX HiRes 2019

This project expects the **ASYX HiRes 2019** dataset to be placed under `data/asyx_hires_2019/raw/`. If your original dataset has a different layout, either reorganize it or extend `scripts/prepare_asyx.py` to map paths into the canonical structure.

### On‑Disk Layout

```
data/asyx_hires_2019/raw/
├─ images/                 # RGB frames (e.g., 000001.jpg)
├─ lidar/                  # LiDAR pointcloud per frame (txt/bin), same stem as image
├─ radar/                  # RADAR pointcloud per frame (txt/bin), same stem as image
├─ calib/                  # camera and sensor calibration
└─ gt/                     # per-frame ground truth
```

### Calibration Files

The following files are expected in `data/asyx_hires_2019/raw/calib/`:

- `camera_intrinsics.txt` — 3×3 intrinsic matrix K (row‑major, whitespace‑separated).
- `camera_distortion.txt` — optional distortion coefficients (k1, k2, p1, p2, [k3...]).
- `lidar_to_cam.txt` — 4×4 extrinsic transform (LiDAR→Camera) as [R|t] in homogeneous form.
- `radar_to_cam.txt` — 4×4 extrinsic transform (RADAR→Camera) as [R|t] in homogeneous form.

### Ground Truth Format

One file per frame under `data/asyx_hires_2019/raw/gt/` with the same stem as the image (e.g., `000123.json`). The evaluation expects a depth field per object (e.g., `center3D_x` when the camera X‑axis encodes forward depth). If your ground truth uses a different field name or axis convention, adjust `configs/asyx_hires_2019.yaml` accordingly.

### Naming Rules

All modalities for a given frame must share the same file stem:
- `images/000123.jpg`
- `lidar/000123.txt` or `.bin`
- `radar/000123.txt` or `.bin`
- `gt/000123.json`

### Build Manifests and Splits

Use the provided script to scan `raw/`, validate files, and produce a manifest and simple splits:

```bash
python scripts/prepare_asyx.py
```

This creates:
- `data/asyx_hires_2019/interim/manifest.csv` — absolute/relative paths per frame (image, lidar, radar, gt, calibration).
- `data/asyx_hires_2019/interim/split.json` — a basic train/val/test split (70/15/15 by default).

You can edit `split.json` for custom experiments.

---

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows:
#   .venv\Scripts\activate
# macOS/Linux:
#   source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

If you plan to develop or contribute, install formatting/lint tools defined in `pyproject.toml` (optional):
```bash
pip install black isort flake8
```

---

## Configuration

Two primary configuration files live in `configs/`:

### `configs/asyx_hires_2019.yaml`

```yaml
dataset:
  manifest: data/asyx_hires_2019/interim/manifest.csv
  split:    data/asyx_hires_2019/interim/split.json

detector:
  model: yolov8x.pt
  classes: [2, 5, 7]         # car, bus, truck
  conf: 0.35                 # confidence threshold
  iou: 0.50                  # NMS IoU
  cache_labels_to: runs/dets # YOLO TXT labels are saved here

projection:
  undistort: true            # use camera_distortion.txt if present
  drop_behind_cam: true      # keep only points with positive forward depth

filtering:
  bbox_point_margin: 0       # points must lie strictly inside the bbox
  depth_axis: x              # camera X-axis encodes forward depth
  summary_stat: median       # robust per-box distance

fusion:
  lidar_weight: 0.80
  radar_weight: 0.20

evaluation:
  metric: [MAE, RMSE]
  gt_depth_key: center3D_x   # field name in GT JSON for depth
```

### `configs/yolov8.yaml`

```yaml
classes: [2, 5, 7]
conf: 0.35
iou: 0.50
agnostic_nms: false
max_det: 300
```

Adjust these values as needed for your experiments.

---

## Quickstart

1) Prepare dataset manifests and splits:
```bash
python scripts/prepare_asyx.py
```

2) Run the pipeline on the **test** split:
```bash
python -m msf_distance.cli \
  --config configs/asyx_hires_2019.yaml \
  --split test \
  --out outputs/
```

Outputs:
- `outputs/metrics_test.json` — MAE/RMSE and summary.
- Optional visualizations or logs (if enabled) under `runs/` and `docs/figures/`.

---

## End‑to‑End Pipeline

### 1) Vehicle Detection (YOLOv8)

- Runs YOLOv8 on frames listed in the chosen split.
- Filters predictions to the specified classes (car, bus, truck) and confidence threshold.
- Caches labels in YOLO‑TXT format under `runs/dets/FRAMEID.txt` for reuse.

Why cache? To make the pipeline reproducible and avoid re‑running detection during iteration.

### 2) 3D→2D Projection

- Load LiDAR and RADAR point clouds for each frame.
- Transform points from sensor frame into camera frame using `lidar_to_cam.txt` and `radar_to_cam.txt`.
- Optionally undistort the image coordinates using `camera_distortion.txt`.
- Project points into the image plane using the intrinsic matrix `camera_intrinsics.txt`.
- Drop points behind the camera if `drop_behind_cam` is true.

### 3) Filter Points Inside Bounding Boxes

- For each detection bbox, select only projected points whose pixel coordinates lie strictly within the box.
- Maintain the original 3D point coordinates so distance calculations are done in 3D, not in pixel units.

### 4) Per‑Box Distance Estimation

- Background points can appear inside a bbox and skew the mean.
- Compute a robust summary statistic per bbox (default: **median**) for each sensor to mitigate outliers.

### 5) Weighted Sensor Fusion

- Combine LiDAR and RADAR distances via a weighted average:
  \n  `fused = w_lidar * |d_lidar| + w_radar * |d_radar|`
- Default weights emphasize LiDAR (0.80) for better distance accuracy while keeping RADAR as supportive. Tune these in `configs/asyx_hires_2019.yaml`.

### 6) Accuracy Evaluation (MAE/RMSE)

- Extract ground truth depths from each frame’s GT JSON (e.g., `center3D_x`).
- Align predicted and GT distance vectors (truncate/pad when counts differ) for a fair comparison.
- Report **MAE** and **RMSE** per split and overall.

---

## Results and Reproducibility

A reference experiment using this pipeline on a subset of ASYX HiRes 2019 achieved the following baseline metrics:

- **MAE:** ~5.49 m  
- **RMSE:** ~6.67 m

These serve as a starting point. Exact values will vary with your split, detection thresholds, calibration fidelity, and fusion weights.

To reproduce:
1. Ensure your dataset is organized as described and manifests are built.
2. Use the provided configs or record the exact configurations you used.
3. Run the pipeline on the same split and save `outputs/metrics_*.json` with your results.

---

## Notebooks

- `notebooks/01_exploration.ipynb` contains exploratory analysis, small‑scale checks, and figures. Use it to verify calibration, visualize projections, and inspect bbox filtering on a few frames.

---

## Troubleshooting

- **No detections saved / empty bboxes:** Verify `configs/yolov8.yaml` class list and confidence threshold; ensure images exist in the chosen split.
- **Projection looks misaligned:** Check calibration matrices, axis conventions, and whether undistortion is required. Ensure transforms are sensor→camera (not camera→sensor).
- **Few or no points inside bboxes:** Confirm that projected points land on the image, bboxes are correct, and you did not drop valid points behind the camera incorrectly.
- **Unrealistic distances:** Inspect the depth axis configuration (`depth_axis: x` by default). Confirm units and sign conventions.
- **Metric mismatch (lengths differ):** The evaluator truncates or pads vectors when the counts of predicted objects and GT differ. Consider stricter detection thresholds or GT matching logic for one‑to‑one evaluation.

---

## Roadmap

- Add per‑object tracking for temporal smoothing.
- Experiment with learned fusion (e.g., small MLP over sensor features).
- Replace bbox filtering with instance segmentation masks for tighter point selection.
- Extend to additional datasets with separate `configs/*.yaml` files.

---

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes. Typical contributions include:
- New projection or fusion strategies.
- Improved evaluation protocols and matching.
- Dataset adapters and calibration loaders.
- Documentation and examples.

---

## License

Specify your chosen license in `LICENSE` (e.g., MIT). If unsure, MIT is a good default for research code.

---

## Citation

If you use this repository in academic or industrial work, please cite the repository and the associated project report in `docs/Sensor_fusion-3.pdf` (if applicable). A `CITATION.cff` file can be added upon request.
