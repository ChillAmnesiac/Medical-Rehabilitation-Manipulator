# 模型验收报告

## 模型信息

- **模型名称**: compatible_wake_word_20260401_114602
- **唤醒词**: marvin
- **训练日期**: 2026-04-01
- **模型大小**: 508.23 KB (520,432 bytes)
- **测试准确率**: 91.15%

---

## 硬性要求检查

### 1. 数据类型 ✓

- **输入 dtype**: `float32` ✓
- **输出 dtype**: `float32` ✓
- **模型类型**: 纯 `float32` ✓
- **Hybrid**: 否 ✓
- **量化**: 无 ✓

### 2. 输入输出 ✓

- **输入 shape**: `[1, 49, 40, 1]` ✓
- **输出 shape**: `[1, 2]` ✓

标签定义:
- `0`: 非唤醒词
- `1`: 唤醒词 marvin

### 3. 算子列表 ✓

**使用的算子 (全部允许):**
- `CONV_2D` ✓
- `MAX_POOL_2D` ✓
- `RESHAPE` (固定尺寸) ✓
- `FULLY_CONNECTED` ✓
- `SOFTMAX` ✓
- `RELU` ✓

### 4. 禁止算子检查 ✓

- **SHAPE**: no ✓
- **MEAN**: no ✓
- **DEQUANTIZE**: no ✓
- **QUANTIZE**: no ✓
- **custom op**: no ✓
- **hybrid**: no ✓
- **动态 shape**: no ✓

---

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

**关键设计**:
- 使用 `Reshape((3840,))` 替代 `Flatten()` 避免 SHAPE 算子
- 不使用 `GlobalAveragePooling2D` 避免 MEAN 算子
- 所有 shape 在编译时确定，无动态 shape

---

## 前处理参数

严格按照 RT-Thread microfrontend 规范:

| 参数 | 值 |
|------|-----|
| 采样率 | 16000 Hz |
| 窗长 | 30 ms (480 samples) |
| 步长 | 20 ms (320 samples) |
| FFT 大小 | 512 |
| Mel 滤波器 | 40 |
| 帧数 | 49 |
| 频率范围 | 125-7500 Hz |

---

## 导出方式

纯 float32 转换，无任何优化:

```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
```

**未使用**以下配置:
- ✗ `converter.optimizations`
- ✗ `converter.representative_dataset`
- ✗ `converter.target_spec.supported_ops`
- ✗ `converter.inference_input_type`
- ✗ `converter.inference_output_type`

---

## 性能指标

- **测试集准确率**: 91.15%
- **测试集精确率**: 91.15%
- **测试集召回率**: 91.15%
- **模型大小**: 508 KB
- **参数量**: 128,866

---

## 交付文件

1. ✓ `model.tflite` - 纯 float32 模型 (508 KB)
2. ✓ `model_data.h` - C 数组头文件 (508 KB)
3. ✓ `best_model.keras` - 最佳 Keras 模型
4. ✓ `final_model.keras` - 最终 Keras 模型
5. ✓ 本验收报告

---

## 验收结论

### 所有硬性要求检查结果:

- ✓ 纯 float32
- ✓ 输入 `[1, 49, 40, 1]`
- ✓ 输出 `[1, 2]`
- ✓ 唤醒词 `marvin`
- ✓ SHAPE = no
- ✓ MEAN = no
- ✓ DEQUANTIZE = no
- ✓ QUANTIZE = no
- ✓ custom op = no
- ✓ hybrid = no
- ✓ 动态 shape = no
- ✓ 有 model.tflite
- ✓ 有 model_data.h
- ✓ 有算子列表

### 最终结论:

**✓ 模型合格，符合所有验收要求**

该模型完全符合 RT-Thread TensorflowLiteMicro-latest 的所有要求，可以交付板端使用。

---

## 板端集成说明

### 预期板端日志

启动后应该看到:

```text
[wake_word] ready model=compatible_wake_word_20260401_114602
[wake_word] input type=float32 shape=[1,49,40,1] output type=float32 shape=[1,2]
[voice_service] wake detector ready=1
```

运行 `wake_on` 后:

```text
[voice_service] detect seq=... len=...
[wake_word] timing mfcc=... invoke=... total=... score=...
[voice_service] wake score=... detected=...
```

**不应该出现:**
- ✗ "Hybrid models are not supported on TFLite Micro"
- ✗ "[wake_word] allocate tensors failed"
- ✗ "Didn't find op for builtin opcode 'SHAPE'"
- ✗ "Didn't find op for builtin opcode 'MEAN'"
- ✗ "DEQUANTIZE operator not supported"

---

## 签名

- **训练端**: wenjunyong666
- **验收时间**: 2026-04-03
- **模型版本**: compatible_wake_word_20260401_114602
- **状态**: ✓ 合格
