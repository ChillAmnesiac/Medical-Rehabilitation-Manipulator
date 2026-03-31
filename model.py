import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

def create_wake_word_model(input_shape=(99, 40, 1), num_classes=2):
    """
    创建轻量级语音唤醒词模型

    参数:
        input_shape: 输入形状 (时间步, MFCC特征数, 通道数)
        num_classes: 分类数量 (2: 唤醒词/非唤醒词)

    返回:
        Keras 模型
    """
    model = keras.Sequential([
        # 输入层
        layers.Input(shape=input_shape),

        # 第一个卷积块
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),

        # 第二个卷积块
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),

        # 第三个卷积块
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.3),

        # 全局平均池化
        layers.GlobalAveragePooling2D(),

        # 全连接层
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),

        # 输出层
        layers.Dense(num_classes, activation='softmax')
    ])

    return model


def create_lightweight_model(input_shape=(99, 40, 1), num_classes=2):
    """
    创建超轻量级模型，适合嵌入式设备
    参数量更少，推理速度更快
    """
    model = keras.Sequential([
        layers.Input(shape=input_shape),

        # 深度可分离卷积
        layers.SeparableConv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        layers.SeparableConv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        layers.GlobalAveragePooling2D(),

        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])

    return model


if __name__ == "__main__":
    # 创建模型
    model = create_wake_word_model()
    model.summary()

    print("\n" + "="*50)
    print("轻量级模型:")
    print("="*50)
    lightweight_model = create_lightweight_model()
    lightweight_model.summary()
