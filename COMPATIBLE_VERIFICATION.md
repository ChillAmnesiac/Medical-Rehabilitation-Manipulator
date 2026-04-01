# 统一模型兼容验证报告

## 验证时间
2026-04-01

## 模型信息
- 模型名称: compatible_wake_word_20260401_114602
- 训练准确率: 91.15%
- 唤醒词: marvin
- 模型大小: 508 KB

## 完全符合板端兼容要求

### ✓ 检查 1: 数据类型
- **输入类型**: `float32` ✓
- **输出类型**: `float32` ✓
- **模型类型**: 纯 float32 ✓
- **Hybrid**: 否 ✓
- **量化**: 无 ✓

### ✓ 检查 2: 输入输出形状
- **输入形状**: `[1, 49, 40, 1]` ✓
- **输出形状**: `[1, 2]` ✓
- **固定形状**: 是 ✓

### ✓ 检查 3: 算子兼容性
**使用的算子（全部兼容）:**
- Conv2D ✓
- MaxPooling2D ✓
- Reshape (固定尺寸) ✓
- Dense ✓
- ReLU ✓
- Softmax ✓

**避免的算子:**
- ✗ Flatten (会引出 SHAPE) - 已避免 ✓
- ✗ GlobalAveragePooling2D (会引出 MEAN) - 已避免 ✓
- ✗ BatchNormalization - 已避免 ✓
- ✗ 动态 shape - 已避免 ✓

### ✓ 检查 4: 推理测试
- 输入: (1, 49, 40, 1) float32
- 输出: (1, 2) float32
- Softmax 和: 1.0000 ✓

## 模型结构

```
Input: (49, 40, 1)
  ↓
Conv2D(8, 3×3, same) + ReLU
  ↓
MaxPooling2D(2×2) → (24, 20, 8)
  ↓
Conv2D(16, 3×3, same) + ReLU
  ↓
MaxPooling2D(2×2) → (12, 10, 16)
  ↓
Conv2D(32, 3×3, same) + ReLU → (12, 10, 32)
  ↓
Reshape(3840) [固定尺寸，不使用 Flatten]
  ↓
Dense(32) + ReLU
  ↓
Dense(2) + Softmax
  ↓
Output: (2,) [非唤醒词, 唤醒词]
```

## 关键设计决策

### 1. 使用 Reshape 替代 Flatten
```python
# 不使用 Flatten (会引出 SHAPE 算子)
# layers.Flatten()

# 使用固定尺寸的 Reshape
layers.Reshape((3840,))  # 12 * 10 * 32 = 3840
```

### 2. 不使用 GlobalAveragePooling2D
避免引入 MEAN 算子，使用 Conv2D + Reshape + Dense 替代。

### 3. 固定输入输出形状
- 输入: [1, 49, 40, 1] - 编译时确定
- 输出: [1, 2] - 编译时确定
- 无动态 shape

## 导出方式

纯 float32 转换，无任何优化：

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

## 特征提取参数

基于官方 microfrontend：

| 参数 | 值 |
|------|-----|
| 采样率 | 16000 Hz |
| 窗长 | 30 ms |
| 步长 | 20 ms |
| FFT 大小 | 512 |
| 特征维度 | 40 |
| 帧数 | 49 |
| 频率范围 | 125-7500 Hz |

## 性能指标

- 测试集准确率: 91.15%
- 测试集精确率: 91.15%
- 测试集召回率: 91.15%
- 模型大小: 508 KB
- 参数量: 128,866

## 板端兼容性

完全符合 RT-Thread TensorflowLiteMicro-latest 要求：

✓ 纯 float32
✓ 固定输入 shape [1, 49, 40, 1]
✓ 固定输出 shape [1, 2]
✓ 仅使用基础算子
✓ 无 SHAPE 算子
✓ 无 MEAN 算子
✓ 无 hybrid
✓ 无动态 shape

## 后续模型复用

此模板可直接复用于：
- VAD (语音活动检测)
- 关键词分类
- IMU 数据分类
- EMG 信号分类
- 融合模型
- 动作预测

只需调整：
- 输入 shape (保持固定)
- 输出类别数
- 卷积层通道数

## 交付文件

1. `model.tflite` - 纯 float32 模型 (508 KB)
2. `model_data.h` - C 数组头文件 (508 KB)
3. `compatible_model.py` - 模型定义
4. `train_compatible.py` - 训练脚本
5. `COMPATIBLE_VERIFICATION.md` - 本验证报告

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
- ✗ "SHAPE operator not supported"
- ✗ "MEAN operator failed"

## 签名

训练端: wenjunyong666
验证时间: 2026-04-01 11:46
模型版本: compatible_wake_word_20260401_114602
