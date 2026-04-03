import sys
from pathlib import Path
import numpy as np
import tensorflow as tf


def verify_model(tflite_path):
    """
    验证 TFLite 模型是否符合板端要求

    检查项:
    1. 数据类型 (必须是 float32)
    2. 输入输出形状 (固定形状)
    3. 算子兼容性 (无 SHAPE, MEAN 等)
    4. 推理测试
    """
    print("="*60)
    print("Model Verification")
    print("="*60)

    tflite_path = Path(tflite_path)
    if not tflite_path.exists():
        print(f"Error: {tflite_path} not found")
        return False

    model_size = tflite_path.stat().st_size
    print(f"\nModel: {tflite_path.name}")
    print(f"Size: {model_size} bytes ({model_size / 1024:.2f} KB)")

    try:
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
    except Exception as e:
        print(f"\n✗ Failed to load model: {e}")
        return False

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    all_passed = True

    # Check 1: Data types
    print("\n" + "="*60)
    print("Check 1: Data Types")
    print("="*60)

    input_dtype = input_details[0]['dtype']
    output_dtype = output_details[0]['dtype']

    print(f"Input type:  {input_dtype}")
    print(f"Output type: {output_dtype}")

    if input_dtype == np.float32 and output_dtype == np.float32:
        print("✓ Both input and output are float32")
    else:
        print("✗ Model is not pure float32")
        all_passed = False

    # Check 2: Input/Output shapes
    print("\n" + "="*60)
    print("Check 2: Input/Output Shapes")
    print("="*60)

    input_shape = input_details[0]['shape']
    output_shape = output_details[0]['shape']

    print(f"Input shape:  {list(input_shape)}")
    print(f"Output shape: {list(output_shape)}")

    expected_input = [1, 49, 40, 1]
    expected_output = [1, 2]

    if list(input_shape) == expected_input:
        print(f"✓ Input shape matches {expected_input}")
    else:
        print(f"✗ Input shape should be {expected_input}")
        all_passed = False

    if list(output_shape) == expected_output:
        print(f"✓ Output shape matches {expected_output}")
    else:
        print(f"✗ Output shape should be {expected_output}")
        all_passed = False

    # Check 3: Operator compatibility
    print("\n" + "="*60)
    print("Check 3: Operator Compatibility")
    print("="*60)

    # Get model details
    with open(tflite_path, 'rb') as f:
        model_content = f.read()

    # Check for problematic operators
    problematic_ops = {
        b'SHAPE': 'SHAPE operator (caused by Flatten)',
        b'MEAN': 'MEAN operator (caused by GlobalAveragePooling2D)',
        b'RESHAPE': None,  # Reshape is OK
    }

    found_issues = []
    for op_bytes, description in problematic_ops.items():
        if op_bytes in model_content:
            if description:
                found_issues.append(description)

    if found_issues:
        print("✗ Found problematic operators:")
        for issue in found_issues:
            print(f"  - {issue}")
        all_passed = False
    else:
        print("✓ No problematic operators detected")
        print("  (SHAPE, MEAN not found)")

    # Check 4: Inference test
    print("\n" + "="*60)
    print("Check 4: Inference Test")
    print("="*60)

    try:
        test_input = np.random.randn(1, 49, 40, 1).astype(np.float32)
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        print(f"Input:  {test_input.shape} {test_input.dtype}")
        print(f"Output: {output.shape} {output.dtype}")
        print(f"Output values: {output[0]}")
        print(f"Softmax sum: {np.sum(output[0]):.4f}")

        if abs(np.sum(output[0]) - 1.0) < 0.01:
            print("✓ Inference successful, softmax sum ≈ 1.0")
        else:
            print("✗ Softmax sum is not close to 1.0")
            all_passed = False

    except Exception as e:
        print(f"✗ Inference failed: {e}")
        all_passed = False

    # Summary
    print("\n" + "="*60)
    print("Verification Summary")
    print("="*60)

    if all_passed:
        print("✓ All checks passed!")
        print("✓ Model is compatible with RT-Thread TensorflowLiteMicro")
        return True
    else:
        print("✗ Some checks failed")
        print("✗ Model may not be compatible with board")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_model.py <model.tflite>")
        print("\nExample:")
        print("  python verify_model.py models/compatible_wake_word/model.tflite")
        return

    tflite_path = sys.argv[1]
    success = verify_model(tflite_path)

    print()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
