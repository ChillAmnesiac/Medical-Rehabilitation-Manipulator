#!/bin/bash
# 快速测试脚本

source ~/tensorflow-env/bin/activate-tf
cd /home/cal/wake_word_model

MODEL_PATH="./models/wake_word_standard_20260331_161432/model.tflite"

echo "================================"
echo "语音唤醒词模型测试"
echo "================================"
echo "模型: $MODEL_PATH"
echo "唤醒词: marvin"
echo ""

# 测试几个样本
python3 << 'EOF'
from inference import WakeWordDetector
import os

model_path = "./models/wake_word_standard_20260331_161432/model.tflite"
detector = WakeWordDetector(model_path, threshold=0.8)

# 测试唤醒词样本
print("测试唤醒词样本:")
wake_dir = "./data/wake_word"
if os.path.exists(wake_dir):
    files = [f for f in os.listdir(wake_dir) if f.endswith('.wav')][:5]
    for file in files:
        path = os.path.join(wake_dir, file)
        is_wake, conf = detector.predict(path)
        status = "✓" if is_wake else "✗"
        print(f"  {status} {file}: {conf:.4f}")

print("\n测试背景音样本:")
bg_dir = "./data/background"
if os.path.exists(bg_dir):
    files = [f for f in os.listdir(bg_dir) if f.endswith('.wav')][:5]
    for file in files:
        path = os.path.join(bg_dir, file)
        is_wake, conf = detector.predict(path)
        status = "✓" if is_wake else "✗"
        print(f"  {status} {file}: {conf:.4f}")
EOF

echo ""
echo "================================"
echo "测试完成"
echo "================================"
