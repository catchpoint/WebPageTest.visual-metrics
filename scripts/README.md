## Usage
Script to Generate comparative data for SI and PerSI CSV/Graphs Data for input videos

### Supported Commands:-

* ** Command to generate CSV raw data
```bash
python generate_data.py  --generate_csv --input_video_dir <input_videos_dir> --output_csv data.csv --visual_metric_file ../visualmetrics.py   
```

* ** Command to generate Graphs from Input CSV 
```bash
python generate_data.py  --generate_graphs --output_csv data.csv --output_dir .
```
