import os
import tensorflow as tf
from tensorflow import keras
import numpy as np
from datetime import datetime
from model import create_wake_word_model, create_lightweight_model
from data_processor import prepare_dataset

def train_model(
    wake_word_dir,
    background_dir,
    model_type='standard',
    epochs=50,
    batch_size=32,
    learning_rate=0.001,
    output_dir='./models'
):
    """
    训练语音唤醒词模型

    参数:
        wake_word_dir: 唤醒词音频目录
        background_dir: 背景音音频目录
        model_type: 模型类型 ('standard' 或 'lightweight')
        epochs: 训练轮数
        batch_size: 批次大小
        learning_rate: 学习率
        output_dir: 模型保存目录
    """
    print("="*60)
    print("开始训练语音唤醒词模型")
    print("="*60)

    # 准备数据集
    print("\n1. 准备数据集...")
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_dataset(
        wake_word_dir, background_dir
    )

    # 转换标签为 one-hot 编码
    y_train = keras.utils.to_categorical(y_train, 2)
    y_val = keras.utils.to_categorical(y_val, 2)
    y_test = keras.utils.to_categorical(y_test, 2)

    # 创建模型
    print(f"\n2. 创建模型 ({model_type})...")
    if model_type == 'lightweight':
        model = create_lightweight_model(input_shape=X_train.shape[1:])
    else:
        model = create_wake_word_model(input_shape=X_train.shape[1:])

    model.summary()

    # 编译模型
    print("\n3. 编译模型...")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_name = f"wake_word_{model_type}_{timestamp}"
    model_path = os.path.join(output_dir, model_name)

    # 回调函数
    callbacks = [
        # 模型检查点
        keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(model_path, 'best_model.keras'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        # 早停
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        # 学习率衰减
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        # TensorBoard
        keras.callbacks.TensorBoard(
            log_dir=os.path.join(model_path, 'logs'),
            histogram_freq=1
        )
    ]

    # 训练模型
    print("\n4. 开始训练...")
    history = model.fit(
        X_train, y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=1
    )

    # 评估模型
    print("\n5. 评估模型...")
    test_loss, test_acc, test_precision, test_recall = model.evaluate(X_test, y_test, verbose=0)
    print(f"测试集准确率: {test_acc:.4f}")
    print(f"测试集精确率: {test_precision:.4f}")
    print(f"测试集召回率: {test_recall:.4f}")
    print(f"测试集损失: {test_loss:.4f}")

    # 保存最终模型
    print("\n6. 保存模型...")
    model.save(os.path.join(model_path, 'final_model.keras'))

    # 转换为 TFLite 格式（用于嵌入式部署）
    print("\n7. 转换为 TFLite 格式...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    tflite_path = os.path.join(model_path, 'model.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"TFLite 模型已保存: {tflite_path}")

    # 保存训练历史
    np.save(os.path.join(model_path, 'history.npy'), history.history)

    print("\n" + "="*60)
    print(f"训练完成！模型已保存到: {model_path}")
    print("="*60)

    return model, history


if __name__ == "__main__":
    # 示例：训练模型
    # 请根据实际情况修改路径
    wake_word_dir = "./data/wake_word"
    background_dir = "./data/background"

    # 训练标准模型
    model, history = train_model(
        wake_word_dir=wake_word_dir,
        background_dir=background_dir,
        model_type='standard',
        epochs=50,
        batch_size=32,
        learning_rate=0.001
    )

    # 或训练轻量级模型
    # model, history = train_model(
    #     wake_word_dir=wake_word_dir,
    #     background_dir=background_dir,
    #     model_type='lightweight',
    #     epochs=50,
    #     batch_size=32,
    #     learning_rate=0.001
    # )
