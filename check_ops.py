#!/usr/bin/env python3
import sys
import struct

def read_tflite_operators(tflite_path):
    """读取 TFLite 模型中的算子列表"""
    with open(tflite_path, 'rb') as f:
        data = f.read()

    # TFLite 使用 FlatBuffers 格式
    # 查找算子代码字符串
    operators = []

    # 常见的 TFLite 算子名称
    op_names = [
        b'CONV_2D', b'DEPTHWISE_CONV_2D', b'MAX_POOL_2D', b'AVERAGE_POOL_2D',
        b'FULLY_CONNECTED', b'SOFTMAX', b'RESHAPE', b'ADD', b'MUL',
        b'RELU', b'RELU6', b'CONCATENATION', b'SHAPE', b'MEAN',
        b'QUANTIZE', b'DEQUANTIZE', b'FLATTEN', b'BATCH_MATMUL',
        b'TRANSPOSE', b'SQUEEZE', b'EXPAND_DIMS', b'PACK', b'UNPACK'
    ]

    found_ops = []
    for op in op_names:
        if op in data:
            found_ops.append(op.decode('utf-8'))

    return found_ops

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_ops.py <model.tflite>")
        sys.exit(1)

    tflite_path = sys.argv[1]
    ops = read_tflite_operators(tflite_path)

    print("Found operators in model:")
    for op in sorted(ops):
        print(f"  - {op}")

    # 检查禁止的算子
    forbidden = ['SHAPE', 'MEAN', 'QUANTIZE', 'DEQUANTIZE', 'FLATTEN']
    found_forbidden = [op for op in ops if op in forbidden]

    if found_forbidden:
        print(f"\n✗ FAILED: Found forbidden operators: {found_forbidden}")
        sys.exit(1)
    else:
        print(f"\n✓ PASSED: No forbidden operators found")
        sys.exit(0)
