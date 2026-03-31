# PSoC 6 Edge E84 Talk 移植指南

## 1. 准备工作

### 硬件要求
- PSoC 6 Edge E84 Talk 开发板
- USB 数据线
- 麦克风（板载）

### 软件要求
- ModusToolbox 3.x
- TensorFlow Lite Micro 库
- ARM GCC 工具链

## 2. 项目设置

### 2.1 创建 ModusToolbox 项目
```bash
# 使用 ModusToolbox IDE 创建新项目
# 选择 PSoC 6 Edge E84 Talk 板型
# 选择 "Empty App" 模板
```

### 2.2 添加 TensorFlow Lite Micro
在项目的 `Makefile` 中添加：
```makefile
# TensorFlow Lite Micro 路径
TFLM_PATH = libs/tensorflow-lite-micro

# 包含路径
INCLUDES += \
    -I$(TFLM_PATH) \
    -I$(TFLM_PATH)/third_party/flatbuffers/include \
    -I$(TFLM_PATH)/third_party/gemmlowp \
    -I$(TFLM_PATH)/third_party/ruy

# 源文件
SOURCES += \
    $(wildcard $(TFLM_PATH)/tensorflow/lite/micro/*.cc) \
    $(wildcard $(TFLM_PATH)/tensorflow/lite/micro/kernels/*.cc) \
    $(wildcard $(TFLM_PATH)/tensorflow/lite/core/api/*.cc)

# 编译选项
CXXFLAGS += -DTF_LITE_STATIC_MEMORY
CXXFLAGS += -DTF_LITE_DISABLE_X86_NEON
```

### 2.3 下载 TensorFlow Lite Micro
```bash
cd <your_project>/libs
git clone https://github.com/tensorflow/tflite-micro.git tensorflow-lite-micro
```

## 3. 集成模型

### 3.1 复制文件
将以下文件复制到项目中：
- `model_data.h` → `source/model_data.h`
- `main.cpp` → `source/main.cpp`

### 3.2 内存配置
在 `wake_word_detector.cc` 中调整内存大小：
```cpp
// 根据实际可用 RAM 调整
constexpr int kTensorArenaSize = 60 * 1024;  // 60KB
```

PSoC 6 有 288KB SRAM，模型大小 468KB (float32，存储在 Flash)，推理需要约 60KB RAM。

## 4. float32 格式说明

模型使用 float32 格式：
- **输入**: float32 张量
- **输出**: float32 张量
- **运算**: 使用浮点运算
- **优势**: 更高的精度，更好的准确率
- **要求**: 需要硬件支持浮点运算（PSoC 6 有 FPU）

## 5. 音频处理

### 4.1 MFCC 特征提取
需要实现 MFCC 提取，可以使用：

**选项 1: ARM CMSIS-DSP**
```cpp
#include "arm_math.h"

void extract_mfcc(const int16_t* audio, int len, float* mfcc) {
    // 1. 预加重
    // 2. 分帧加窗
    // 3. FFT
    // 4. Mel 滤波器组
    // 5. DCT
}
```

**选项 2: 使用现成库**
- [microMFCC](https://github.com/StuartIanNaylor/microMFCC)
- [kissfft](https://github.com/mborgerding/kissfft)

### 4.2 麦克风采集
```cpp
#include "cyhal_pdm_pcm.h"

cyhal_pdm_pcm_t pdm_pcm;
int16_t audio_buffer[16000];  // 1秒 @ 16kHz

void init_microphone() {
    cyhal_pdm_pcm_cfg_t pdm_pcm_cfg = {
        .sample_rate = 16000,
        .decimation_rate = 64,
        .mode = CYHAL_PDM_PCM_MODE_STEREO,
        .word_length = 16,
        .left_gain = 0,
        .right_gain = 0,
    };

    cyhal_pdm_pcm_init(&pdm_pcm, PDM_DATA, PDM_CLK,
                       &audio_clock, &pdm_pcm_cfg);
}

void get_audio_from_mic(int16_t* buffer, int len) {
    cyhal_pdm_pcm_read(&pdm_pcm, buffer, &len);
}
```

## 5. 优化建议

### 5.1 量化模型（减小尺寸）
在训练时使用量化：
```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]  # 或 tf.int8
tflite_model = converter.convert()
```

### 5.2 降低内存使用
- 减少模型层数
- 使用深度可分离卷积
- 降低特征维度

### 5.3 实时处理
```cpp
// 使用滑动窗口，避免重复计算
#define FRAME_SHIFT 160  // 10ms @ 16kHz
#define FRAME_SIZE 512   // 32ms

// 每次只处理新的音频帧
```

## 6. 编译和烧录

### 6.1 编译
```bash
make build
```

### 6.2 烧录
```bash
make program
```

### 6.3 调试
```bash
make debug
```

## 7. 性能指标

预期性能（PSoC 6 @ 150MHz）：
- 推理时间: ~50-100ms
- 内存使用: ~528KB Flash (模型 468KB) + ~60KB RAM (推理)
- 功耗: ~10-20mA (活动模式)
- 精度: float32 高精度

## 8. 故障排查

### 内存不足
- 减小 `kTensorArenaSize`
- 模型存储在 Flash，不占用 RAM
- 优化模型结构

### 推理速度慢
- 启用 ARM CMSIS-NN 优化
- 使用硬件加速（如果可用）
- 降低输入分辨率

### 识别率低
- 调整检测阈值
- 增加训练数据
- 添加噪声抑制

## 9. 完整项目结构

```
psoc6_wake_word/
├── source/
│   ├── main.cpp
│   ├── model_data.h
│   ├── audio_processing.cpp
│   └── audio_processing.h
├── libs/
│   └── tensorflow-lite-micro/
├── Makefile
└── README.md
```

## 10. 参考资源

- [TensorFlow Lite Micro 文档](https://www.tensorflow.org/lite/microcontrollers)
- [PSoC 6 文档](https://www.infineon.com/cms/en/product/microcontroller/32-bit-psoc-arm-cortex-microcontroller/psoc-6-32-bit-arm-cortex-m4-mcu/)
- [ModusToolbox 用户指南](https://www.infineon.com/cms/en/design-support/tools/sdk/modustoolbox-software/)
