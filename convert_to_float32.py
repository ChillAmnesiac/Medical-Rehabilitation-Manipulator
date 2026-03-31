"""
将模型转换为纯 float32 格式
适用于支持浮点运算的嵌入式设备
"""
import tensorflow as tf
import numpy as np

def convert_to_float32_tflite(model_path, output_path):
    """
    转换模型为 float32 格式

    参数:
        model_path: Keras 模型路径
        output_path: 输出 TFLite 模型路径
    """
    print("="*60)
    print("转换模型为 float32 格式")
    print("="*60)

    # 加载模型
    print("\n1. 加载模型...")
    model = tf.keras.models.load_model(model_path)
    print(f"   模型加载成功: {model_path}")

    # 创建转换器
    print("\n2. 配置转换器...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # 不进行任何优化，保持 float32
    # converter.optimizations = []  # 不优化

    # 确保使用 float32
    converter.target_spec.supported_types = [tf.float32]

    # 转换
    print("\n3. 执行转换...")
    try:
        tflite_model = converter.convert()
    except Exception as e:
        print(f"错误: 转换失败 - {e}")
        return False

    # 保存
    print("\n4. 保存 float32 模型...")
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    # 显示信息
    model_size = len(tflite_model)
    print(f"\n✓ float32 模型已保存: {output_path}")
    print(f"  模型大小: {model_size} 字节 ({model_size/1024:.2f} KB)")

    # 验证模型
    print("\n5. 验证 float32 模型...")
    interpreter = tf.lite.Interpreter(model_path=output_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"  输入类型: {input_details[0]['dtype']}")
    print(f"  输出类型: {output_details[0]['dtype']}")
    print(f"  输入形状: {input_details[0]['shape']}")
    print(f"  输出形状: {output_details[0]['shape']}")

    if input_details[0]['dtype'] == np.float32 and output_details[0]['dtype'] == np.float32:
        print("  ✓ 模型使用 float32 格式")
    else:
        print("  ⚠ 警告: 模型可能包含非 float32 操作")

    print("\n" + "="*60)
    print("转换完成！")
    print("="*60)

    return True


if __name__ == "__main__":
    # 转换模型
    keras_model = "./models/wake_word_standard_20260331_161432/best_model.keras"
    float32_model = "./models/wake_word_standard_20260331_161432/model_float32.tflite"

    success = convert_to_float32_tflite(keras_model, float32_model)

    if success:
        print("\n下一步:")
        print("1. 运行 python convert_to_c.py 生成新的 C 数组")
        print("2. PSoC 6 代码将使用 float32 推理")
