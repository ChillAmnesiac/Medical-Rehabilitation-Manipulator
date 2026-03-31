"""
将 TFLite 模型转换为 C 数组，用于嵌入式部署
"""
import numpy as np

def convert_tflite_to_c_array(tflite_path, output_path, array_name="model_data"):
    """
    将 TFLite 模型转换为 C 数组

    参数:
        tflite_path: TFLite 模型路径
        output_path: 输出 C 头文件路径
        array_name: C 数组名称
    """
    # 读取 TFLite 模型
    with open(tflite_path, 'rb') as f:
        model_data = f.read()

    # 转换为字节数组
    model_bytes = np.frombuffer(model_data, dtype=np.uint8)

    # 生成 C 头文件
    with open(output_path, 'w') as f:
        f.write(f"// Auto-generated model file\n")
        f.write(f"// Model size: {len(model_bytes)} bytes\n\n")
        f.write(f"#ifndef MODEL_DATA_H\n")
        f.write(f"#define MODEL_DATA_H\n\n")
        f.write(f"const unsigned int {array_name}_len = {len(model_bytes)};\n")
        f.write(f"const unsigned char {array_name}[] = {{\n")

        # 每行写入 12 个字节
        for i in range(0, len(model_bytes), 12):
            chunk = model_bytes[i:i+12]
            hex_values = ', '.join([f'0x{b:02x}' for b in chunk])
            f.write(f"  {hex_values},\n")

        f.write(f"}};\n\n")
        f.write(f"#endif  // MODEL_DATA_H\n")

    print(f"✓ C 数组已生成: {output_path}")
    print(f"  模型大小: {len(model_bytes)} 字节 ({len(model_bytes)/1024:.2f} KB)")


if __name__ == "__main__":
    # 转换模型（按照要求读取 model.tflite）
    tflite_model = "./models/wake_word_standard_20260331_161432/model.tflite"
    output_file = "./psoc6_deployment/model_data.h"

    import os
    os.makedirs("./psoc6_deployment", exist_ok=True)

    convert_tflite_to_c_array(tflite_model, output_file, "wake_word_model")
