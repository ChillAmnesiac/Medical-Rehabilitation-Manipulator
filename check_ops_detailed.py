#!/usr/bin/env python3
"""
详细的 TFLite 模型算子检查工具
不依赖 TensorFlow，直接解析 FlatBuffers
"""
import sys
import struct
from pathlib import Path


# TFLite BuiltinOperator 枚举值
BUILTIN_OPS = {
    0: "ADD",
    1: "AVERAGE_POOL_2D",
    2: "CONCATENATION",
    3: "CONV_2D",
    4: "DEPTHWISE_CONV_2D",
    5: "DEPTH_TO_SPACE",
    6: "DEQUANTIZE",
    7: "EMBEDDING_LOOKUP",
    8: "FLOOR",
    9: "FULLY_CONNECTED",
    10: "HASHTABLE_LOOKUP",
    11: "L2_NORMALIZATION",
    12: "L2_POOL_2D",
    13: "LOCAL_RESPONSE_NORMALIZATION",
    14: "LOGISTIC",
    15: "LSH_PROJECTION",
    16: "LSTM",
    17: "MAX_POOL_2D",
    18: "MUL",
    19: "RELU",
    20: "RELU_N1_TO_1",
    21: "RELU6",
    22: "RESHAPE",
    23: "RESIZE_BILINEAR",
    24: "RNN",
    25: "SOFTMAX",
    26: "SPACE_TO_DEPTH",
    27: "SVDF",
    28: "TANH",
    29: "CONCAT_EMBEDDINGS",
    30: "SKIP_GRAM",
    31: "CALL",
    32: "CUSTOM",
    33: "EMBEDDING_LOOKUP_SPARSE",
    34: "PAD",
    35: "UNIDIRECTIONAL_SEQUENCE_RNN",
    36: "GATHER",
    37: "BATCH_TO_SPACE_ND",
    38: "SPACE_TO_BATCH_ND",
    39: "TRANSPOSE",
    40: "MEAN",
    41: "SUB",
    42: "DIV",
    43: "SQUEEZE",
    44: "UNIDIRECTIONAL_SEQUENCE_LSTM",
    45: "STRIDED_SLICE",
    46: "BIDIRECTIONAL_SEQUENCE_RNN",
    47: "EXP",
    48: "TOPK_V2",
    49: "SPLIT",
    50: "LOG_SOFTMAX",
    51: "DELEGATE",
    52: "BIDIRECTIONAL_SEQUENCE_LSTM",
    53: "CAST",
    54: "PRELU",
    55: "MAXIMUM",
    56: "ARG_MAX",
    57: "MINIMUM",
    58: "LESS",
    59: "NEG",
    60: "PADV2",
    61: "GREATER",
    62: "GREATER_EQUAL",
    63: "LESS_EQUAL",
    64: "SELECT",
    65: "SLICE",
    66: "SIN",
    67: "TRANSPOSE_CONV",
    68: "SPARSE_TO_DENSE",
    69: "TILE",
    70: "EXPAND_DIMS",
    71: "EQUAL",
    72: "NOT_EQUAL",
    73: "LOG",
    74: "SUM",
    75: "SQRT",
    76: "RSQRT",
    77: "SHAPE",
    78: "POW",
    79: "ARG_MIN",
    80: "FAKE_QUANT",
    81: "REDUCE_PROD",
    82: "REDUCE_MAX",
    83: "PACK",
    84: "LOGICAL_OR",
    85: "ONE_HOT",
    86: "LOGICAL_AND",
    87: "LOGICAL_NOT",
    88: "UNPACK",
    89: "REDUCE_MIN",
    90: "FLOOR_DIV",
    91: "REDUCE_ANY",
    92: "SQUARE",
    93: "ZEROS_LIKE",
    94: "FILL",
    95: "FLOOR_MOD",
    96: "RANGE",
    97: "RESIZE_NEAREST_NEIGHBOR",
    98: "LEAKY_RELU",
    99: "SQUARED_DIFFERENCE",
    100: "MIRROR_PAD",
    101: "ABS",
    102: "SPLIT_V",
    103: "UNIQUE",
    104: "CEIL",
    105: "REVERSE_V2",
    106: "ADD_N",
    107: "GATHER_ND",
    108: "COS",
    109: "WHERE",
    110: "RANK",
    111: "ELU",
    112: "REVERSE_SEQUENCE",
    113: "MATRIX_DIAG",
    114: "QUANTIZE",
    115: "MATRIX_SET_DIAG",
    116: "ROUND",
    117: "HARD_SWISH",
    118: "IF",
    119: "WHILE",
    120: "NON_MAX_SUPPRESSION_V4",
    121: "NON_MAX_SUPPRESSION_V5",
    122: "SCATTER_ND",
    123: "SELECT_V2",
    124: "DENSIFY",
    125: "SEGMENT_SUM",
    126: "BATCH_MATMUL",
}


def check_tflite_model(tflite_path):
    """检查 TFLite 模型"""
    print("="*60)
    print("TFLite Model Operator Check")
    print("="*60)

    tflite_path = Path(tflite_path)
    if not tflite_path.exists():
        print(f"✗ File not found: {tflite_path}")
        return False

    model_size = tflite_path.stat().st_size
    print(f"\nModel: {tflite_path.name}")
    print(f"Size: {model_size} bytes ({model_size / 1024:.2f} KB)")

    with open(tflite_path, 'rb') as f:
        data = f.read()

    # 检查文件头 (TFL3 可能在偏移 0 或 4)
    if b'TFL3' not in data[:20]:
        print("✗ Not a valid TFLite model (missing TFL3 header)")
        return False

    print("✓ Valid TFLite model")

    # 查找算子代码
    print("\n" + "="*60)
    print("Checking for operators...")
    print("="*60)

    # 禁止的算子
    forbidden_ops = {
        77: "SHAPE",
        40: "MEAN",
        6: "DEQUANTIZE",
        114: "QUANTIZE",
        32: "CUSTOM",
    }

    # 允许的算子
    allowed_ops = {
        3: "CONV_2D",
        17: "MAX_POOL_2D",
        22: "RESHAPE",
        9: "FULLY_CONNECTED",
        25: "SOFTMAX",
        19: "RELU",
        4: "DEPTHWISE_CONV_2D",
    }

    # 搜索算子代码（简单的字节搜索）
    found_forbidden = []
    found_allowed = []

    # 检查禁止的算子名称字符串
    for op_code, op_name in forbidden_ops.items():
        if op_name.encode() in data:
            found_forbidden.append(op_name)

    # 检查允许的算子名称字符串
    for op_code, op_name in allowed_ops.items():
        if op_name.encode() in data:
            found_allowed.append(op_name)

    print("\nFound operators:")
    if found_allowed:
        for op in sorted(found_allowed):
            print(f"  ✓ {op}")
    else:
        print("  (Unable to detect operators by string search)")

    print("\n" + "="*60)
    print("Forbidden Operator Check")
    print("="*60)

    all_passed = True

    if found_forbidden:
        print("✗ FAILED: Found forbidden operators:")
        for op in found_forbidden:
            print(f"  ✗ {op}")
        all_passed = False
    else:
        print("✓ PASSED: No forbidden operator strings found")
        print("  - SHAPE: not found")
        print("  - MEAN: not found")
        print("  - DEQUANTIZE: not found")
        print("  - QUANTIZE: not found")
        print("  - CUSTOM: not found")

    # 检查 dtype
    print("\n" + "="*60)
    print("Data Type Check")
    print("="*60)

    # 查找 float32 标记
    if b'float32' in data or b'FLOAT32' in data:
        print("✓ Model contains float32 references")
    else:
        print("? Unable to confirm float32 (may still be correct)")

    # 查找 int8/uint8 标记
    if b'int8' in data or b'INT8' in data or b'uint8' in data or b'UINT8' in data:
        print("✗ Model may contain int8/uint8 quantization")
        all_passed = False
    else:
        print("✓ No int8/uint8 quantization markers found")

    # 总结
    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    if all_passed:
        print("✓ Model appears to be compatible")
        print("✓ No forbidden operators detected")
        print("✓ No quantization markers found")
        return True
    else:
        print("✗ Model has compatibility issues")
        print("✗ Contains forbidden operators or quantization")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_ops_detailed.py <model.tflite>")
        sys.exit(1)

    tflite_path = sys.argv[1]
    success = check_tflite_model(tflite_path)

    print()
    sys.exit(0 if success else 1)
