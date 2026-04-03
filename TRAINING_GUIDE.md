# 另一台电脑训练执行说明

## 目的

在另一台电脑上训练新的唤醒词模型，并生成可给板端使用的：

- `model.tflite`
- `model_data.h`

当前唤醒词固定为：`marvin`

---

## 一、代码位置

训练代码已经上传到 GitHub 仓库 `wake-word-model` 分支里的：

- `training_package/`

主要文件：

- `training_package/train_wake_word.py`
- `training_package/verify_model.py`
- `training_package/convert_to_c.py`
- `training_package/requirements.txt`
- `training_package/README.md`

---

## 二、环境准备

建议：Python `3.10` 或 `3.11`

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r training_package\requirements.txt
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r training_package/requirements.txt
```

---

## 三、数据目录

在仓库根目录准备下面结构：

```text
dataset/
  positive/
  negative/
  noise/
```

含义：

- `positive/`：唤醒词 `marvin` 的 wav
- `negative/`：其他词或非唤醒词 wav
- `noise/`：噪声 wav

音频要求：

- wav 格式
- 单声道
- 16kHz 采样率
- 1 秒左右时长

推荐数据量：

- positive: 100+ 样本
- negative: 500+ 样本
- noise: 10+ 样本

---

## 四、训练

在仓库根目录执行：

### Windows

```powershell
python training_package\train_wake_word.py
```

### Linux / macOS

```bash
python training_package/train_wake_word.py
```

训练完成后会生成：

- `models/compatible_wake_word/best_model.keras`
- `models/compatible_wake_word/final_model.keras`
- `models/compatible_wake_word/model.tflite`
- `models/compatible_wake_word/history.npy`

---

## 五、验证模型

训练完成后执行：

### Windows

```powershell
python training_package\verify_model.py models\compatible_wake_word\model.tflite
```

### Linux / macOS

```bash
python training_package/verify_model.py models/compatible_wake_word/model.tflite
```

希望看到的关键结果：

- ✓ 输入 dtype：`float32`
- ✓ 输出 dtype：`float32`
- ✓ 输入 shape：`[1, 49, 40, 1]`
- ✓ 输出 shape：`[1, 2]`
- ✓ 无 SHAPE 算子
- ✓ 无 MEAN 算子
- ✓ 推理测试通过

注意：

- `verify_model.py` 只能做训练侧快速检查
- 最终是否真的兼容板端，还要把模型交回板端再验证

---

## 六、导出 C 数组

执行：

### Windows

```powershell
python training_package\convert_to_c.py models\compatible_wake_word\model.tflite
```

### Linux / macOS

```bash
python training_package/convert_to_c.py models/compatible_wake_word/model.tflite
```

执行后会在 `models/compatible_wake_word/` 目录生成：

- `model_data.h`

---

## 七、最后需要交付回来

请把下面两个文件发回来或上传到 GitHub：

1. `models/compatible_wake_word/model.tflite`
2. `models/compatible_wake_word/model_data.h`

如果方便，也一起保留：

3. `models/compatible_wake_word/best_model.keras`
4. `models/compatible_wake_word/final_model.keras`

---

## 八、快速执行流程

```bash
# 1. 克隆仓库并切换分支
git clone <repo_url>
cd <repo_name>
git checkout wake-word-model

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r training_package/requirements.txt

# 3. 准备数据集
mkdir -p dataset/positive dataset/negative dataset/noise
# 将音频文件放入对应目录

# 4. 训练模型
python training_package/train_wake_word.py

# 5. 验证模型
python training_package/verify_model.py models/compatible_wake_word/model.tflite

# 6. 导出 C 数组
python training_package/convert_to_c.py models/compatible_wake_word/model.tflite

# 7. 交付文件
# - models/compatible_wake_word/model.tflite
# - models/compatible_wake_word/model_data.h
```

---

## 九、常见问题

### 训练准确率低

- 增加 positive 样本数量
- 增加 negative 样本多样性
- 调整学习率
- 增加训练轮数

### 模型验证失败

- 检查是否使用了正确的训练脚本
- 确认 TensorFlow 版本 >= 2.15.0
- 重新训练模型

### 板端加载失败

- 运行 verify_model.py 检查兼容性
- 确认模型是 float32
- 确认无 SHAPE/MEAN 算子
- 联系板端开发人员

---

## 十、给训练同学的一句话

```text
请在 wake-word-model 分支根目录准备 dataset/positive、dataset/negative、dataset/noise 三个目录，然后安装 training_package/requirements.txt，执行 train_wake_word.py 训练，再执行 verify_model.py 检查输入输出，最后执行 convert_to_c.py 生成 model_data.h，并把 model.tflite 和 model_data.h 回传。
```
