import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def create_compatible_model(input_shape=(49, 40, 1), num_classes=2):
    """
    创建完全兼容板端的唤醒词模型

    严格遵守约束:
    - 不使用 Flatten (会引出 SHAPE)
    - 不使用 GlobalAveragePooling2D (会引出 MEAN)
    - 使用 Reshape 并明确指定固定尺寸
    - 只使用基础算子: Conv2D, MaxPooling2D, Dense, Reshape, ReLU, Softmax

    参数:
        input_shape: (49, 40, 1) - 固定输入形状
        num_classes: 2 - 二分类

    返回:
        Keras 模型
    """

    # 计算 Reshape 的目标尺寸
    # Input: (49, 40, 1)
    # Conv2D + MaxPool(2,2): (49, 40) -> (24, 20)
    # Conv2D + MaxPool(2,2): (24, 20) -> (12, 10)
    # Conv2D: (12, 10, 32)
    # Reshape 目标: 12 * 10 * 32 = 3840

    model = keras.Sequential([
        # 输入层 - 固定为 (49, 40, 1)
        layers.Input(shape=input_shape),

        # 第一个卷积块
        layers.Conv2D(8, (3, 3), padding='same', activation='relu'),
        layers.MaxPooling2D((2, 2)),

        # 第二个卷积块
        layers.Conv2D(16, (3, 3), padding='same', activation='relu'),
        layers.MaxPooling2D((2, 2)),

        # 第三个卷积块
        layers.Conv2D(32, (3, 3), padding='same', activation='relu'),

        # Reshape - 明确指定固定尺寸 (不使用 Flatten)
        # 当前形状: (12, 10, 32) = 3840
        layers.Reshape((3840,)),

        # 全连接层
        layers.Dense(32, activation='relu'),

        # 输出层 - 二分类
        layers.Dense(num_classes, activation='softmax')
    ])

    return model


if __name__ == "__main__":
    # 创建模型
    model = create_compatible_model()
    model.summary()

    print("\n模型信息:")
    print(f"  输入形状: (49, 40, 1)")
    print(f"  输出形状: (2,)")
    print(f"  参数量: {model.count_params():,}")

    # 验证 Reshape 尺寸
    print("\n层信息:")
    for i, layer in enumerate(model.layers):
        print(f"  [{i}] {layer.name}: {layer.__class__.__name__}")
        if hasattr(layer, 'output_shape'):
            print(f"      输出形状: {layer.output_shape}")
