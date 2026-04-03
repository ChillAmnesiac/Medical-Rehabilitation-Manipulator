# 唤醒词模型训练包

完全兼容 RT-Thread TensorflowLiteMicro-latest 的唤醒词模型训练工具。

## 系统要求

- Python 3.8+
- CUDA 11.8+ (GPU 训练)
- 8GB+ RAM
- 10GB+ 磁盘空间

## 安装

```bash
pip install -r requirements.txt
```

## 数据集准备

创建以下目录结构:

```
dataset/
├── positive/     # 唤醒词音频 (*.wav)
├── negative/     # 非唤醒词音频 (*.wav)
└── noise/        # 背景噪声 (*.wav)
```

音频要求:
- 格式: WAV
- 采样率: 16000 Hz (自动重采样)
- 时长: 1 秒 (自动裁剪/填充)
- 声道: 单声道 (自动转换)

推荐数据量:
- positive: 100+ 样本
- negative: 500+ 样本
- noise: 10+ 样本

## 训练模型

```bash
python train_wake_word.py
```

训练完成后会生成:
- `models/compatible_wake_word/best_model.keras` - 最佳模型
- `models/compatible_wake_word/final_model.keras` - 最终模型
- `models/compatible_wake_word/model.tflite` - TFLite 模型
- `models/compatible_wake_word/history.npy` - 训练历史

## 验证模型

```bash
python verify_model.py models/compatible_wake_word/model.tflite
```

检查项:
- ✓ 数据类型 (float32)
- ✓ 输入形状 [1, 49, 40, 1]
- ✓ 输出形状 [1, 2]
- ✓ 无 SHAPE 算子
- ✓ 无 MEAN 算子
- ✓ 推理测试

## 转换为 C 数组

```bash
python convert_to_c.py models/compatible_wake_word/model.tflite
```

生成 `model_data.h` 文件，可直接嵌入固件。

## 模型参数

### 音频特征
- 采样率: 16000 Hz
- 窗长: 30 ms (480 samples)
- 步长: 20 ms (320 samples)
- FFT 大小: 512
- Mel 滤波器: 40
- 帧数: 49
- 频率范围: 125-7500 Hz

### 模型结构
```
Input: (49, 40, 1)
  ↓
Conv2D(8, 3×3) + ReLU
  ↓
MaxPooling2D(2×2)
  ↓
Conv2D(16, 3×3) + ReLU
  ↓
MaxPooling2D(2×2)
  ↓
Conv2D(32, 3×3) + ReLU
  ↓
Reshape(3840)  # 固定尺寸，不使用 Flatten
  ↓
Dense(32) + ReLU
  ↓
Dense(2) + Softmax
  ↓
Output: (2,) [非唤醒词, 唤醒词]
```

### 数据增强
- 随机增益: 0.8-1.2x
- 时间偏移: ±800 samples
- 噪声混合: 2-3% 强度

## 板端兼容性

严格遵守约束:
- ✓ 纯 float32 (无量化)
- ✓ 固定输入 [1, 49, 40, 1]
- ✓ 固定输出 [1, 2]
- ✓ 使用 Reshape 替代 Flatten
- ✓ 不使用 GlobalAveragePooling2D
- ✓ 不使用 BatchNormalization
- ✓ 无动态 shape

支持的算子:
- Conv2D
- MaxPooling2D
- Reshape (固定尺寸)
- Dense
- ReLU
- Softmax

## 常见问题

### 训练准确率低
- 增加 positive 样本数量
- 增加 negative 样本多样性
- 调整学习率
- 增加训练轮数

### 模型过大
- 减少卷积层通道数
- 减少全连接层神经元数
- 当前模型: ~508 KB

### 板端加载失败
- 运行 verify_model.py 检查兼容性
- 确认模型是 float32
- 确认无 SHAPE/MEAN 算子

## 文件说明

- `train_wake_word.py` - 训练脚本
- `convert_to_c.py` - TFLite 转 C 数组
- `verify_model.py` - 模型验证工具
- `requirements.txt` - Python 依赖

## 许可证

MIT License
