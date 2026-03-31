import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def create_microfrontend_model(input_shape=(49, 40, 1), num_classes=2):
    """
    创建符合官方 microfrontend 要求的轻量级模型

    参数:
        input_shape: (49, 40, 1) - 固定输入形状
        num_classes: 2 - 二分类（background, wake_word）

    返回:
        Keras 模型
    """
    model = keras.Sequential([
        # 输入层 - 固定为 (49, 40, 1)
        layers.Input(shape=input_shape),

        # 第一个卷积块
        layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),

        # 第二个卷积块
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),

        # 第三个卷积块
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),

        # 展平
        layers.Flatten(),

        # 全连接层
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),

        # 输出层 - 二分类
        layers.Dense(num_classes, activation='softmax')
    ])

    return model


if __name__ == "__main__":
    # 创建模型
    model = create_microfrontend_model()
    model.summary()

    print("\n模型信息:")
    print(f"  输入形状: (49, 40, 1)")
    print(f"  输出形状: (2,)")
    print(f"  参数量: {model.count_params():,}")
