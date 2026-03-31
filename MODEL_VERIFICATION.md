# 模型导出验证报告

## 验证时间
2026-03-31

## 验证结果

### ✓ 检查 1: 文件名
- 文件名: `model.tflite`
- 位置: `./models/wake_word_standard_20260331_161432/model.tflite`
- 状态: **通过**

### ✓ 检查 2: 输入输出类型
- 输入类型: `float32`
- 输出类型: `float32`
- 状态: **通过**

### ✓ 检查 3: 量化参数
- 输入量化: `(0.0, 0)` - 无量化
- 输出量化: `(0.0, 0)` - 无量化
- 状态: **通过**

### ✓ 检查 4: 模型结构
- 输入形状: `[1, 101, 40, 1]`
- 输出形状: `[1, 2]`
- 状态: **通过**

### ✓ 检查 5: C 数组生成
- 文件: `./psoc6_deployment/model_data.h`
- 大小: 478892 字节 (467.67 KB)
- 文件末尾: 正确（包含 `};` 和 `#endif`）
- 状态: **通过**

### ✓ 检查 6: 转换脚本
- `convert_to_c.py` 读取: `model.tflite`
- 状态: **通过**

## 导出方式

使用纯 float32 转换，无任何优化或量化：

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

## 板端兼容性

该模型符合 RT-Thread TensorflowLiteMicro-latest 的要求：

- ✓ 纯 float32 模型
- ✓ 非 hybrid 模型
- ✓ MEAN 节点使用 float32 输入
- ✓ 不会触发 "Hybrid models are not supported" 错误

## 交付文件

1. `model.tflite` - 纯 float32 模型
2. `convert_to_c.py` - C 数组转换脚本
3. `psoc6_deployment/model_data.h` - C 数组头文件

## 预期板端日志

启动后应该看到：

```text
[wake_word] ready model=...
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

## 验证命令

```bash
# 验证模型类型
python3 << 'EOF'
import tensorflow as tf
import numpy as np

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

assert input_details[0]['dtype'] == np.float32, "输入不是 float32"
assert output_details[0]['dtype'] == np.float32, "输出不是 float32"
assert input_details[0]['quantization'] == (0.0, 0), "输入有量化"
assert output_details[0]['quantization'] == (0.0, 0), "输出有量化"

print("✓ 验证通过：纯 float32 模型")
EOF
```

## 签名

训练端: wenjunyong666
验证时间: 2026-03-31
模型版本: wake_word_standard_20260331_161432
