import sys
from pathlib import Path


def convert_tflite_to_c(tflite_path, output_path, array_name="g_model"):
    """
    将 TFLite 模型转换为 C 数组头文件

    Args:
        tflite_path: TFLite 模型文件路径
        output_path: 输出的 .h 文件路径
        array_name: C 数组名称
    """
    tflite_path = Path(tflite_path)
    output_path = Path(output_path)

    if not tflite_path.exists():
        print(f"Error: {tflite_path} not found")
        return False

    with open(tflite_path, "rb") as f:
        model_data = f.read()

    model_size = len(model_data)
    print(f"Model size: {model_size} bytes ({model_size / 1024:.2f} KB)")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(f"// Auto-generated from {tflite_path.name}\n")
        f.write(f"// Model size: {model_size} bytes\n\n")
        f.write(f"#ifndef MODEL_DATA_H\n")
        f.write(f"#define MODEL_DATA_H\n\n")
        f.write(f"const unsigned char {array_name}[] = {{\n")

        for i in range(0, model_size, 12):
            chunk = model_data[i:i+12]
            hex_values = ", ".join(f"0x{b:02x}" for b in chunk)
            f.write(f"  {hex_values},\n")

        f.write(f"}};\n\n")
        f.write(f"const unsigned int {array_name}_len = {model_size};\n\n")
        f.write(f"#endif  // MODEL_DATA_H\n")

    print(f"C header file saved to: {output_path}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_c.py <model.tflite> [output.h] [array_name]")
        print("\nExample:")
        print("  python convert_to_c.py models/compatible_wake_word/model.tflite")
        print("  python convert_to_c.py model.tflite model_data.h g_model")
        return

    tflite_path = sys.argv[1]

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = Path(tflite_path).parent / "model_data.h"

    array_name = sys.argv[3] if len(sys.argv) >= 4 else "g_model"

    print("="*60)
    print("TFLite to C Array Converter")
    print("="*60)
    print(f"Input:  {tflite_path}")
    print(f"Output: {output_path}")
    print(f"Array:  {array_name}")
    print()

    success = convert_tflite_to_c(tflite_path, output_path, array_name)

    if success:
        print("\n" + "="*60)
        print("Conversion completed!")
        print("="*60)
    else:
        print("\nConversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
