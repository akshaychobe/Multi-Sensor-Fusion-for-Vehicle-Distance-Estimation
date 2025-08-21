import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW  = ROOT / "dataset_astyx_hires2019" / "raw"
OUT  = ROOT / "dataset_astyx_hires2019" / "interim"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    images = sorted((RAW / "images").glob("*.*"))
    if not images:
        print("No images found under dataset_astyx_hires2019/raw/images. Populate dataset first.")
        return

    rows = []
    for img in images:
        stem = img.stem
        rows.append({
            "frame_id": stem,
            "image_path": str(img),
            "lidar_path": str((RAW / "lidar" / f"{stem}").with_suffix(".txt")),
            "radar_path": str((RAW / "radar" / f"{stem}").with_suffix(".txt")),
            "gt_path":    str((RAW / "gt"    / f"{stem}").with_suffix(".json")),
            "K_path":     str(RAW / "calib" / "camera_intrinsics.txt"),
            "D_path":     str(RAW / "calib" / "camera_distortion.txt"),
            "T_lidar_cam_path": str(RAW / "calib" / "lidar_to_cam.txt"),
            "T_radar_cam_path": str(RAW / "calib" / "radar_to_cam.txt"),
        })

    man_csv = OUT / "manifest.csv"
    with man_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

    n = len(rows); tr = int(0.70*n); va = int(0.85*n)
    (OUT / "split.json").write_text(json.dumps({
        "train": [r["frame_id"] for r in rows[:tr]],
        "val":   [r["frame_id"] for r in rows[tr:va]],
        "test":  [r["frame_id"] for r in rows[va:]],
    }, indent=2))

    print(f"[OK] Wrote {man_csv} and split.json with {n} frames")

if __name__ == "__main__":
    main()
