# 语音唤醒词模型 - Wake Word Detection

基于 TensorFlow 的语音唤醒词检测系统，支持嵌入式设备部署（PSoC 6）。

## 项目简介

本项目实现了一个轻量级的语音唤醒词检测模型，使用 "marvin" 作为唤醒词。模型基于卷积神经网络（CNN），可以部署到嵌入式设备上。

## 特性

- 轻量级 CNN 模型（~134KB，int8 量化）
- 准确率 93%+
- 完全 int8 量化，无浮点运算
- 支持 TensorFlow Lite Micro
- 可部署到 PSoC 6 Edge E84 Talk
- 包含完整的训练和推理代码

## 项目结构

```
wake_word_model/
├── model.py              # 模型定义
├── data_processor.py     # 数据处理
├── train.py              # 训练脚本
├── inference.py          # 推理脚本
├── prepare_data.py       # 数据准备
├── convert_to_c.py       # 模型转换
├── requirements.txt      # Python 依赖
├── psoc6_deployment/     # PSoC 6 部署代码
│   ├── model_data.h      # 模型 C 数组
│   ├── wake_word_detector.h/.cc
│   ├── audio_processing.h/.cc
│   ├── main.cc
│   ├── Makefile
│   └── README.md
└── models/               # 训练好的模型
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv tensorflow-env
source tensorflow-env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据准备

```bash
# 下载 Google Speech Commands 数据集
bash download_data.sh

# 准备训练数据
python prepare_data.py
```

### 3. 训练模型

```bash
python train.py
```

### 4. 测试模型

```bash
python inference.py
```

### 5. 转换为 int8 量化格式

```bash
python convert_to_int8.py
```

### 6. 转换为嵌入式 C 数组

```bash
python convert_to_c.py
```

## PSoC 6 部署

详细的部署指南请参考 `psoc6_deployment/README.md`。

### 快速步骤

1. 在 ModusToolbox 中创建项目
2. 复制 `psoc6_deployment/` 下的文件到项目
3. 集成 TensorFlow Lite Micro 库
4. 编译并烧录

## 模型性能

- **准确率**: 93.05%
- **精确率**: 93.05%
- **召回率**: 93.05%
- **模型大小**: 134KB (int8 量化)
- **推理时间**: ~50-100ms (PSoC 6 @ 150MHz)
- **量化格式**: 完全 int8，无浮点运算

## 技术栈

- TensorFlow 2.21+
- TensorFlow Lite Micro
- Python 3.12
- librosa (音频处理)
- PSoC 6 HAL

## 训练数据

使用 Google Speech Commands Dataset v0.02：
- 唤醒词样本: 500 个 "marvin"
- 背景音样本: 1000+ 个其他词汇

## 许可证

MIT License

## 作者

wenjunyong666

## 致谢

- Google Speech Commands Dataset
- TensorFlow Lite Micro
- Infineon PSoC 6
