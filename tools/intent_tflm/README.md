# Intent TFLM training bundle

This directory packages the EMG intent model training datasets, scripts-related outputs, and quantization results for TensorFlow Lite Micro deployment.

## Layout

- `datasets/`: cleaned window CSVs used for training (not raw capture streams)
- `results/`: trained model artifacts, metrics, TFLite float/int8 models, quantization reports
- `docs/`: training result notes

## Companion scripts in `tools/`

| Script | Role |
|---|---|
| `train_intent_tf.py` | Train Keras intent model + export TFLite |
| `prepare_clean_intent_windows.py` | Clean/merge window CSVs and optional elbow_curl merge |
| `quantize_intent_tf.py` | PTQ export path |
| `quantize_intent_tflite_int8.py` | Full-int8 TFLite quantization |
| `eval_tflite_intent.py` | Evaluate float/int8 TFLite accuracy |
| `export_tflite_c_array.py` | Export `.tflite` as C array for TFLM |
| `export_tflm_golden_samples.py` | Golden int8 samples for device smoke tests |
| `infer_intent_tf.py` | Host-side Keras inference |

## Primary run (2026-07-18, 3-class)

- Dataset: `datasets/S01_day4_20260714_20260718_windows_elbow_curl_cleaned.csv`
- Results: `results/S01_day4_20260714_20260718_elbow_curl_cleaned/`
- Classes: `elbow_curl`, `rest`, `shoulder_flex`
- Float test accuracy: ~98.81%
- Full-int8 model: `intent_model_full_int8.tflite`

## Retrain example

```bash
python tools/train_intent_tf.py \
  --input tools/intent_tflm/datasets/S01_day4_20260714_20260718_windows_elbow_curl_cleaned.csv \
  --output-dir tools/intent_tflm/results/retrain_demo

python tools/quantize_intent_tflite_int8.py \
  --model-dir tools/intent_tflm/results/S01_day4_20260714_20260718_elbow_curl_cleaned \
  --input tools/intent_tflm/datasets/S01_day4_20260714_20260718_windows_elbow_curl_cleaned.csv
```

Note: large raw capture CSVs remain under local `data/sensor_capture/` and are gitignored.
