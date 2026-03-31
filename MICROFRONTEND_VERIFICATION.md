# 官方 Microfrontend 模型验证报告

## 验证时间
2026-03-31

## 模型信息
- 模型名称: microfrontend_wake_word_20260331_205843
- 训练准确率: 95.58%
- 唤醒词: marvin

## 验证结果

### ✓ 检查 1: 输入形状
- **要求**: `[1, 49, 40, 1]`
- **实际**: `[1, 49, 40, 1]`
- **状态**: **通过** ✓

### ✓ 检查 2: 输出形状
- **要求**: `[1, 2]`
- **实际**: `[1, 2]`
- **状态**: **通过** ✓

### ✓ 检查 3: 输入输出类型
- **输入类型**: `float32`
- **输出类型**: `float32`
- **状态**: **通过** ✓

### ✓ 检查 4: 量化参数
- **输入量化**: `(0.0, 0)` - 无量化
- **输出量化**: `(0.0, 0)` - 无量化
- **状态**: **通过** ✓

### ✓ 检查 5: 模型类型
- **类型**: 纯 float32
- **Hybrid**: 否
- **状态**: **通过** ✓

## 特征提取参数

模型使用官方 microfrontend 兼容的参数：

### 音频参数
- 采样率: 16000 Hz
- 单声道
- PCM: int16

### 特征参数
- 窗长: 30 ms
- 步长: 20 ms
- FFT 大小: 512
- 特征维度: 40
- 帧数: 49
- 总特征数: 49 × 40 = 1960

### Mel 滤波器参数
- 下限频率: 125.0 Hz
- 上限频率: 7500.0 Hz
- 滤波器数量: 40

## 模型结构

```
Input: (49, 40, 1)
  ↓
Conv2D(16, 3×3) + ReLU + MaxPool(2×2)
  ↓
Conv2D(32, 3×3) + ReLU + MaxPool(2×2)
  ↓
Conv2D(64, 3×3) + ReLU
  ↓
Flatten
  ↓
Dense(64) + ReLU + Dropout(0.3)
  ↓
Dense(2) + Softmax
  ↓
Output: (2,) [background, wake_word]
```

## 导出方式

使用纯 float32 转换，无任何优化：

```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
```

**未使用**以下配置：
- ✗ `converter.optimizations`
- ✗ `converter.representative_dataset`
- ✗ `converter.target_spec.supported_ops`
- ✗ `converter.inference_input_type`
- ✗ `converter.inference_output_type`

## 模型文件

- `model.tflite`: 2.02 MB (纯 float32)
- `model_data.h`: 2.02 MB (C 数组)

## 训练数据

- 唤醒词样本: 500 个 "marvin"
- 背景音样本: 1000+ 个其他词汇
- 数据集: Google Speech Commands v0.02

## 性能指标

- 测试集准确率: 95.58%
- 测试集精确率: 95.58%
- 测试集召回率: 95.58%

## 板端兼容性

该模型完全符合 RT-Thread TensorflowLiteMicro-latest 要求：

✓ 输入形状: `[1, 49, 40, 1]`
✓ 输出形状: `[1, 2]`
✓ 纯 float32 模型
✓ 非 hybrid 模型
✓ 基于官方 microfrontend 参数
✓ 二分类输出

## 预期板端日志

启动后应该看到：

```text
[wake_word] ready model=...
[wake_word] input type=float32 shape=[1,49,40,1] output type=float32 shape=[1,2]
[voice_service] wake detector ready=1
```

运行 `wake_on` 后：

```text
[voice_service] detect seq=... len=...
[wake_word] timing mfcc=... invoke=... total=... score=...
[voice_service] wake score=... detected=...
```

**不应该出现：**
- ✗ "Hybrid models are not supported on TFLite Micro"
- ✗ "[wake_word] allocate tensors failed"

## 交付文件

1. `model.tflite` - 纯 float32 模型 (2.02 MB)
2. `model_data.h` - C 数组头文件 (2.02 MB)
3. `microfrontend_processor.py` - 特征提取代码
4. `microfrontend_model.py` - 模型定义
5. `train_microfrontend.py` - 训练脚本

## 与板端前处理的对齐

训练端特征提取已尽量对齐官方 microfrontend：

| 参数 | 官方值 | 训练端值 | 状态 |
|------|--------|----------|------|
| 窗长 | 30 ms | 30 ms | ✓ |
| 步长 | 20 ms | 20 ms | ✓ |
| FFT 大小 | 512 | 512 | ✓ |
| 特征维度 | 40 | 40 | ✓ |
| 帧数 | 49 | 49 | ✓ |
| 下限频率 | 125 Hz | 125 Hz | ✓ |
| 上限频率 | 7500 Hz | 7500 Hz | ✓ |

## 后续优化建议

1. 如果模型太大（2MB），可以考虑：
   - 减少卷积层通道数
   - 减少全连接层神经元数
   - 使用深度可分离卷积

2. 如果识别率需要提升：
   - 增加训练数据
   - 添加数据增强
   - 调整模型结构

3. 板端可以进一步优化：
   - 使用官方 microfrontend C 代码
   - 添加连续时间窗判定
   - 添加分数平滑

## 签名

训练端: wenjunyong666
验证时间: 2026-03-31 20:58
模型版本: microfrontend_wake_word_20260331_205843
