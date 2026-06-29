$ErrorActionPreference = "Stop"

Set-Location "D:\medical-rehab-manipulator-product"

Write-Host "Starting VLA mono capture preview..."
Write-Host "Default camera: 2"
Write-Host "Default output: D:\vla_dataset"
Write-Host "Controls in preview window: Space=save, a=auto, q=quit"

python .\scripts\collect_stereo_dataset.py `
  --mode mono `
  --camera 2 `
  --backend dshow `
  --out D:\vla_dataset `
  --baseline-m 0.06 `
  --flip-left none
