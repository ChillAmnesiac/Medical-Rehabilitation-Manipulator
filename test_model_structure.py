#!/usr/bin/env python3
"""
测试模型结构，不需要真实数据
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def create_model_no_shape_v1(input_shape=(49, 40, 1), num_classes=2):
    """方案1：使用 batch_size=1 + Reshape"""
    model = keras.Sequential([
        layers.Input(shape=input_shape, batch_size=1),

        layers.Conv2D(8, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(16, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(32, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(64, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(64, (3, 2), padding="valid", activation="relu"),

        layers.Conv2D(32, (1, 1), activation="relu"),
        layers.Conv2D(num_classes, (1, 1), activation=None),

        layers.Reshape((num_classes,)),
        layers.Softmax(),
    ])
    return model


def create_model_no_shape_v2(input_shape=(49, 40, 1), num_classes=2):
    """方案2：完全用卷积，不用 Reshape"""
    inputs = layers.Input(shape=input_shape)

    x = layers.Conv2D(8, (3, 3), padding="same", activation="relu")(inputs)
    x = layers.MaxPooling2D((2, 2))(x)

    x = layers.Conv2D(16, (3, 3), padding="same", activation="relu")(x)
    x = layers.MaxPooling2D((2, 2))(x)

    x = layers.Conv2D(32, (3, 3), padding="same", activation="relu")(x)
    x = layers.MaxPooling2D((2, 2))(x)

    x = layers.Conv2D(64, (3, 3), padding="same", activation="relu")(x)
    x = layers.MaxPooling2D((2, 2))(x)

    x = layers.Conv2D(64, (3, 2), padding="valid", activation="relu")(x)  # (1, 1, 64)

    # 用 1x1 卷积代替 Dense
    x = layers.Conv2D(32, (1, 1), activation="relu")(x)
    logits = layers.Conv2D(num_classes, (1, 1), activation=None)(x)  # (1, 1, 2)

    # 用 Squeeze 去掉空间维度
    logits_squeezed = tf.squeeze(logits, axis=[1, 2])  # (batch, 2)

    outputs = layers.Softmax()(logits_squeezed)

    model = keras.Model(inputs=inputs, outputs=outputs)
    return model


def test_model(model, model_name):
    print("\n" + "="*60)
    print(f"Testing: {model_name}")
    print("="*60)

    model.summary()

    # 导出为 TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    tflite_path = f"/tmp/test_{model_name}.tflite"
    with open(tflite_path, "wb") as f:
        f.write(tflite_model)

    print(f"\nModel exported to: {tflite_path}")
    print(f"Model size: {len(tflite_model)} bytes ({len(tflite_model)/1024:.2f} KB)")

    # 加载并检查算子
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"\nInput: {input_details[0]['shape']} {input_details[0]['dtype']}")
    print(f"Output: {output_details[0]['shape']} {output_details[0]['dtype']}")

    # 检查算子
    with open(tflite_path, 'rb') as f:
        model_content = f.read()

    from tensorflow.lite.python import schema_py_generated as schema_fb
    model_fb = schema_fb.Model.GetRootAsModel(model_content, 0)

    subgraph = model_fb.Subgraphs(0)
    operators = []

    for i in range(subgraph.OperatorsLength()):
        op = subgraph.Operators(i)
        opcode_index = op.OpcodeIndex()
        opcode = model_fb.OperatorCodes(opcode_index)
        builtin_code = opcode.BuiltinCode()

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
            45: "STRIDED_SLICE",
            83: "PACK",
            43: "SQUEEZE",
        }

        op_name = op_names.get(builtin_code, f"UNKNOWN_{builtin_code}")
        operators.append((builtin_code, op_name))

    print("\nOperators:")
    for code, name in operators:
        print(f"  - {name}")

    # 检查禁止的算子
    forbidden = {77: "SHAPE", 40: "MEAN", 6: "DEQUANTIZE", 114: "QUANTIZE"}
    found_forbidden = [name for code, name in operators if code in forbidden]

    if found_forbidden:
        print(f"\n✗ FAILED: Found forbidden operators: {found_forbidden}")
        return False
    else:
        print(f"\n✓ PASSED: No forbidden operators")
        return True


def main():
    print("="*60)
    print("Model Structure Test")
    print("="*60)

    # 测试方案1
    try:
        model_v1 = create_model_no_shape_v1()
        result_v1 = test_model(model_v1, "v1_batch_size_reshape")
    except Exception as e:
        print(f"\n✗ V1 failed: {e}")
        result_v1 = False

    # 测试方案2
    try:
        model_v2 = create_model_no_shape_v2()
        result_v2 = test_model(model_v2, "v2_conv_only")
    except Exception as e:
        print(f"\n✗ V2 failed: {e}")
        result_v2 = False

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"V1 (batch_size + Reshape): {'✓ PASSED' if result_v1 else '✗ FAILED'}")
    print(f"V2 (Conv only): {'✓ PASSED' if result_v2 else '✗ FAILED'}")


if __name__ == "__main__":
    main()
