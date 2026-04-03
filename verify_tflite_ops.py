#!/usr/bin/env python3
"""
使用 TensorFlow 真正检查 TFLite 模型中的算子
"""
import sys
import tensorflow as tf
import numpy as np


def check_tflite_operators(tflite_path):
    """使用 TensorFlow Lite Interpreter 检查模型算子"""
    print("="*60)
    print("TFLite Model Operator Verification")
    print("="*60)
    print(f"\nModel: {tflite_path}")

    # 加载模型
    try:
        interpreter = tf.lite.Interpreter(model_path=tflite_path)
        interpreter.allocate_tensors()
    except Exception as e:
        print(f"\n✗ Failed to load model: {e}")
        return False

    # 获取输入输出详情
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print("\n" + "="*60)
    print("1. Input/Output Check")
    print("="*60)

    input_shape = input_details[0]['shape'].tolist()
    output_shape = output_details[0]['shape'].tolist()
    input_dtype = input_details[0]['dtype']
    output_dtype = output_details[0]['dtype']

    print(f"Input shape:  {input_shape}")
    print(f"Input dtype:  {input_dtype}")
    print(f"Output shape: {output_shape}")
    print(f"Output dtype: {output_dtype}")

    all_passed = True

    # 检查 shape
    if input_shape != [1, 49, 40, 1]:
        print(f"✗ Input shape should be [1, 49, 40, 1], got {input_shape}")
        all_passed = False
    else:
        print("✓ Input shape correct")

    if output_shape != [1, 2]:
        print(f"✗ Output shape should be [1, 2], got {output_shape}")
        all_passed = False
    else:
        print("✓ Output shape correct")

    # 检查 dtype
    if input_dtype != np.float32:
        print(f"✗ Input dtype should be float32, got {input_dtype}")
        all_passed = False
    else:
        print("✓ Input dtype correct (float32)")

    if output_dtype != np.float32:
        print(f"✗ Output dtype should be float32, got {output_dtype}")
        all_passed = False
    else:
        print("✓ Output dtype correct (float32)")

    # 获取模型详情
    print("\n" + "="*60)
    print("2. Operator List")
    print("="*60)

    # 读取模型文件获取算子信息
    with open(tflite_path, 'rb') as f:
        model_content = f.read()

    # 使用 flatbuffers 解析（如果可用）
    try:
        from tensorflow.lite.python import schema_py_generated as schema_fb
        model = schema_fb.Model.GetRootAsModel(model_content, 0)

        # 获取算子代码
        subgraph = model.Subgraphs(0)
        operators = []

        for i in range(subgraph.OperatorsLength()):
            op = subgraph.Operators(i)
            opcode_index = op.OpcodeIndex()
            opcode = model.OperatorCodes(opcode_index)
            builtin_code = opcode.BuiltinCode()

            # TFLite builtin operator codes
            op_names = {
                3: "CONV_2D",
                4: "DEPTHWISE_CONV_2D",
                9: "FULLY_CONNECTED",
                17: "MAX_POOL_2D",
                19: "RELU",
                22: "RESHAPE",
                25: "SOFTMAX",
                40: "MEAN",
                77: "SHAPE",
                6: "DEQUANTIZE",
                114: "QUANTIZE",
            }

            op_name = op_names.get(builtin_code, f"UNKNOWN_{builtin_code}")
            operators.append((builtin_code, op_name))

        print("\nFound operators:")
        for code, name in operators:
            print(f"  - {name} (code: {code})")

        # 检查禁止的算子
        print("\n" + "="*60)
        print("3. Forbidden Operator Check")
        print("="*60)

        forbidden = {
            77: "SHAPE",
            40: "MEAN",
            6: "DEQUANTIZE",
            114: "QUANTIZE",
        }

        found_forbidden = []
        for code, name in operators:
            if code in forbidden:
                found_forbidden.append(name)

        if found_forbidden:
            print("✗ FAILED: Found forbidden operators:")
            for op in found_forbidden:
                print(f"  ✗ {op}")
            all_passed = False
        else:
            print("✓ PASSED: No forbidden operators")
            print("  - SHAPE: not found")
            print("  - MEAN: not found")
            print("  - DEQUANTIZE: not found")
            print("  - QUANTIZE: not found")

        # 检查是否只使用允许的算子
        allowed = {3, 4, 9, 17, 19, 22, 25}  # CONV_2D, DEPTHWISE_CONV_2D, FULLY_CONNECTED, MAX_POOL_2D, RELU, RESHAPE, SOFTMAX

        print("\n" + "="*60)
        print("4. Allowed Operator Check")
        print("="*60)

        disallowed = []
        for code, name in operators:
            if code not in allowed:
                disallowed.append(name)

        if disallowed:
            print("✗ WARNING: Found operators not in allowed list:")
            for op in disallowed:
                print(f"  ! {op}")
        else:
            print("✓ All operators are in allowed list")

    except Exception as e:
        print(f"✗ Could not parse operator details: {e}")
        print("  (This may indicate a problem with the model)")
        all_passed = False

    # 推理测试
    print("\n" + "="*60)
    print("5. Inference Test")
    print("="*60)

    try:
        test_input = np.random.randn(1, 49, 40, 1).astype(np.float32)
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        print(f"✓ Inference successful")
        print(f"  Output shape: {output.shape}")
        print(f"  Output dtype: {output.dtype}")
        print(f"  Output values: {output[0]}")
        print(f"  Softmax sum: {np.sum(output[0]):.6f}")

        if abs(np.sum(output[0]) - 1.0) > 0.01:
            print("✗ WARNING: Softmax sum is not close to 1.0")
    except Exception as e:
        print(f"✗ Inference failed: {e}")
        all_passed = False

    # 总结
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)

    if all_passed:
        print("✓ MODEL PASSED ALL CHECKS")
        print("✓ Model is compatible with RT-Thread TFLite Micro")
        return True
    else:
        print("✗ MODEL FAILED")
        print("✗ Model is NOT compatible with RT-Thread TFLite Micro")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python verify_tflite_ops.py <model.tflite>")
        sys.exit(1)

    tflite_path = sys.argv[1]
    success = check_tflite_operators(tflite_path)

    print()
    sys.exit(0 if success else 1)
