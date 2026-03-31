import os
import tensorflow as tf
from tensorflow import keras
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split

from microfrontend_model import create_microfrontend_model
from microfrontend_processor import MicrofrontendProcessor

def train_microfrontend_model(
    wake_word_dir,
    background_dir,
    epochs=50,
    batch_size=32,
    learning_rate=0.001,
    output_dir='./models'
):
    """
    训练基于官方 microfrontend 的唤醒词模型

    参数:
        wake_word_dir: 唤醒词音频目录
        background_dir: 背景音音频目录
        epochs: 训练轮数
        batch_size: 批次大小
        learning_rate: 学习率
        output_dir: 模型保存目录
    """
    print("="*60)
    print("训练基于官方 microfrontend 的唤醒词模型")
    print("="*60)

    # 1. 准备数据集
    print("\n1. 准备数据集...")
    processor = MicrofrontendProcessor()
    X, y = processor.load_dataset(wake_word_dir, background_dir)

    # 分割数据集
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )

    # 转换标签为 one-hot 编码
    y_train = keras.utils.to_categorical(y_train, 2)
    y_val = keras.utils.to_categorical(y_val, 2)
    y_test = keras.utils.to_categorical(y_test, 2)

    print(f"\n训练集: {len(X_train)} 样本")
    print(f"验证集: {len(X_val)} 样本")
    print(f"测试集: {len(X_test)} 样本")

    # 2. 创建模型
    print(f"\n2. 创建模型...")
    model = create_microfrontend_model(input_shape=(49, 40, 1))
    model.summary()

    # 3. 编译模型
    print("\n3. 编译模型...")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_name = f"microfrontend_wake_word_{timestamp}"
    model_path = os.path.join(output_dir, model_name)
    os.makedirs(model_path, exist_ok=True)

    # 回调函数
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(model_path, 'best_model.keras'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]

    # 4. 训练模型
    print("\n4. 开始训练...")
    history = model.fit(
        X_train, y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1
    )

    # 5. 评估模型
    print("\n5. 评估模型...")
    test_loss, test_acc, test_precision, test_recall = model.evaluate(X_test, y_test, verbose=0)
    print(f"测试集准确率: {test_acc:.4f}")
    print(f"测试集精确率: {test_precision:.4f}")
    print(f"测试集召回率: {test_recall:.4f}")

    # 6. 保存最终模型
    print("\n6. 保存模型...")
    model.save(os.path.join(model_path, 'final_model.keras'))

    # 7. 导出为 TFLite（纯 float32）
    print("\n7. 导出为 TFLite 格式...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # 不使用任何优化，保持纯 float32
    tflite_model = converter.convert()

    tflite_path = os.path.join(model_path, 'model.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"TFLite 模型已保存: {tflite_path}")

    # 8. 验证 TFLite 模型
    print("\n8. 验证 TFLite 模型...")
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"  输入类型: {input_details[0]['dtype']}")
    print(f"  输入形状: {input_details[0]['shape']}")
    print(f"  输出类型: {output_details[0]['dtype']}")
    print(f"  输出形状: {output_details[0]['shape']}")
    print(f"  量化参数: {input_details[0]['quantization']}")

    # 保存训练历史
    np.save(os.path.join(model_path, 'history.npy'), history.history)

    print("\n" + "="*60)
    print(f"训练完成！模型已保存到: {model_path}")
    print("="*60)

    return model, history, model_path


if __name__ == "__main__":
    # 训练模型
    wake_word_dir = "./data/wake_word"
    background_dir = "./data/background"

    model, history, model_path = train_microfrontend_model(
        wake_word_dir=wake_word_dir,
        background_dir=background_dir,
        epochs=50,
        batch_size=32,
        learning_rate=0.001
    )

    print(f"\n下一步:")
    print(f"1. 运行 python convert_to_c.py 生成 model_data.h")
    print(f"2. 模型路径: {model_path}/model.tflite")
