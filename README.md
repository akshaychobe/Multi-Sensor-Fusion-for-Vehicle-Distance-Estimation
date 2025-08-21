# Multi-Sensor Fusion for Vehicle Distance Estimation (ASYX HiRes 2019)

This repository implements a step-by-step, dataset-aware pipeline for estimating distances to vehicles
by combining camera detections (YOLOv8) with LiDAR and RADAR point clouds. The primary dataset is
ASYX HiRes 2019. The pipeline includes detection, sensor projection to image plane, bounding-box
filtering, robust per-box distance estimation, weighted fusion, and MAE/RMSE evaluation.

This repository starts minimal and will grow in small, focused commits.
