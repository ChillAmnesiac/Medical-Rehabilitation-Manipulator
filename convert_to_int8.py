"""
将模型转换为 int8 量化格式
适用于不支持浮点运算的嵌入式设备
"""
import tensorflow as tf
import numpy as np
from data_processor import AudioDataProcessor

def representative_dataset_gen():
    """
    生成代表性数据集用于量化校准
    """
    processor = AudioDataProcessor()

    # 从训练数据中采样
    wake_word_dir = "./data/wake_word"
    background_dir = "./data/background"

    import os
    files = []

    # 收集一些样本
    if os.path.exists(wake_word_dir):
        wake_files = [os.path.join(wake_word_dir, f)
                     for f in os.listdir(wake_word_dir)
                     if f.endswith('.wav')][:50]
        files.extend(wake_files)

    if os.path.exists(background_dir):
        bg_files = [os.path.join(background_dir, f)
                   for f in os.listdir(background_dir)
                   if f.endswith('.wav')][:50]
        files.extend(bg_files)

    print(f"使用 {len(files)} 个样本进行量化校准...")

    for file_path in files:
        try:
            # 处理音频
            mfcc = processor.process_audio_file(file_path)
            mfcc = np.expand_dims(mfcc, axis=0)
            mfcc = np.expand_dims(mfcc, axis=-1)
            yield [mfcc.astype(np.float32)]
        except Exception as e:
            print(f"处理 {file_path} 时出错: {e}")
            continue


def convert_to_int8_tflite(model_path, output_path):
    """
    转换模型为 int8 量化格式

    参数:
        model_path: Keras 模型路径
        output_path: 输出 TFLite 模型路径
    """
    print("="*60)
    print("转换模型为 int8 量化格式")
    print("="*60)

    # 加载模型
    print("\n1. 加载模型...")
    model = tf.keras.models.load_model(model_path)
    print(f"   模型加载成功: {model_path}")

    # 创建转换器
    print("\n2. 配置转换器...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # 设置优化选项 - 完全 int8 量化
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # 设置输入输出为 int8
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    # 提供代表性数据集用于校准
    print("\n3. 生成代表性数据集用于量化校准...")
    converter.representative_dataset = representative_dataset_gen

    # 转换
    print("\n4. 执行量化转换...")
    try:
        tflite_model = converter.convert()
    except Exception as e:
        print(f"错误: 转换失败 - {e}")
        return False

    # 保存
    print("\n5. 保存量化模型...")
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    # 显示信息
    original_size = len(tflite_model)
    print(f"\n✓ int8 量化模型已保存: {output_path}")
    print(f"  模型大小: {original_size} 字节 ({original_size/1024:.2f} KB)")

    # 验证模型
    print("\n6. 验证量化模型...")
    interpreter = tf.lite.Interpreter(model_path=output_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"  输入类型: {input_details[0]['dtype']}")
    print(f"  输出类型: {output_details[0]['dtype']}")
    print(f"  输入形状: {input_details[0]['shape']}")
    print(f"  输出形状: {output_details[0]['shape']}")

    if input_details[0]['dtype'] == np.int8 and output_details[0]['dtype'] == np.int8:
        print("  ✓ 模型已完全量化为 int8")
    else:
        print("  ⚠ 警告: 模型可能包含非 int8 操作")

    print("\n" + "="*60)
    print("转换完成！")
    print("="*60)

    return True


if __name__ == "__main__":
    # 转换模型
    keras_model = "./models/wake_word_standard_20260331_161432/best_model.keras"
    int8_model = "./models/wake_word_standard_20260331_161432/model_int8.tflite"

    success = convert_to_int8_tflite(keras_model, int8_model)

    if success:
        print("\n下一步:")
        print("1. 运行 python convert_to_c.py 生成新的 C 数组")
        print("2. 更新 PSoC 6 代码以使用 int8 推理")
