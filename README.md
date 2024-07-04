# Multi-Sensor Fusion for Vehicle Distance Estimation
=====================================================

## Introduction

This project aims to develop a **multi-sensor fusion** approach for estimating vehicle distances in images. The system leverages **YOLOv8** for object detection, **LiDAR** and **RADAR** point clouds for 3D information, and a **weighted average** of LiDAR and RADAR distances for robust distance estimation.

## Methodology

The project consists of the following steps:

### 1. Object Detection with YOLOv8

The script utilizes a pre-trained **YOLOv8x** model to detect vehicles in images.

### 2. Point Cloud Projection

The script transforms 3D points from the **LiDAR** and **RADAR** sensors onto the corresponding 2D image plane.

### 3. Filtering Points in Bounding Boxes

The script filters the projected points that lie within the detected bounding boxes and visualizes them.

### 4. Estimating Distances

The script estimates the distance of the detected vehicles within each bounding box using the **LiDAR** and **RADAR** data.

### 5. Weighted Average Sensor Fusion

The script refines distance estimates by fusing **LiDAR** and **RADAR** data using a weighted average method.

### 6. Accuracy Evaluation

The script assesses the accuracy of the distance estimates using **Mean Absolute Error (MAE)** and **Root Mean Square Error (RMSE)** metrics.

## Results

The evaluation resulted in a **Mean Absolute Error (MAE)** of 5.49 meters and a **Root Mean Square Error (RMSE)** of 6.67 meters. These values suggest that, on average, the distance estimates were generally within 5.49 meters of the actual distances.

## Code

The code for this project is written in **Python** and is available in the [code.ipynb](code.ipynb) file.

## Dataset

The dataset used for this project consists of images, **LiDAR** and **RADAR** point cloud data, and ground truth 3D bounding box distances. The dataset is available in the [data/](data/) folder.
