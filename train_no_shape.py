import os
import random
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers


SAMPLE_RATE = 16000
DURATION_SEC = 1.0
TARGET_SAMPLES = int(SAMPLE_RATE * DURATION_SEC)

N_FFT = 512
WIN_LENGTH = 480          # 30 ms
HOP_LENGTH = 320          # 20 ms
N_MELS = 40
TARGET_FRAMES = 49

DATASET_DIR = Path("dataset")
POSITIVE_DIR = DATASET_DIR / "positive"
NEGATIVE_DIR = DATASET_DIR / "negative"
NOISE_DIR = DATASET_DIR / "noise"

MODEL_DIR = Path("models") / "no_shape_wake_word"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


def load_audio(path):
    audio, sr = sf.read(path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if sr != SAMPLE_RATE:
        audio = librosa.resample(audio.astype(np.float32), orig_sr=sr, target_sr=SAMPLE_RATE)
    return audio.astype(np.float32)


def fix_length(audio):
    if len(audio) < TARGET_SAMPLES:
        audio = np.pad(audio, (0, TARGET_SAMPLES - len(audio)))
    else:
        audio = audio[:TARGET_SAMPLES]
    return audio.astype(np.float32)


def add_noise(audio, noise_pool, noise_scale=0.03):
    if not noise_pool:
        return audio
    noise = random.choice(noise_pool)
    noise = fix_length(noise)
    mixed = audio + noise_scale * noise
    return np.clip(mixed, -1.0, 1.0)


def time_shift(audio, shift_max=800):
    shift = random.randint(-shift_max, shift_max)
    if shift == 0:
        return audio
    if shift > 0:
        return np.pad(audio[:-shift], (shift, 0))
    shift = -shift
    return np.pad(audio[shift:], (0, shift))


def random_gain(audio, min_gain=0.8, max_gain=1.2):
    gain = random.uniform(min_gain, max_gain)
    return np.clip(audio * gain, -1.0, 1.0)


def extract_features(audio):
    audio = fix_length(audio)

    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        win_length=WIN_LENGTH,
        n_mels=N_MELS,
        fmin=125,
        fmax=7500,
        power=2.0,
    )

    feat = librosa.power_to_db(mel, ref=np.max).T

    if feat.shape[0] < TARGET_FRAMES:
        pad = np.zeros((TARGET_FRAMES - feat.shape[0], feat.shape[1]), dtype=np.float32)
        feat = np.concatenate([feat, pad], axis=0)
    else:
        feat = feat[:TARGET_FRAMES, :]

    feat = feat.astype(np.float32)
    mean = np.mean(feat)
    std = np.std(feat) + 1e-6
    feat = (feat - mean) / std
    feat = np.expand_dims(feat, axis=-1)   # (49, 40, 1)
    return feat


def collect_files(folder):
    if not folder.exists():
        return []
    files = []
    for ext in ("*.wav", "*.WAV"):
        files.extend(folder.glob(ext))
    return sorted(files)


def build_dataset():
    positive_files = collect_files(POSITIVE_DIR)
    negative_files = collect_files(NEGATIVE_DIR)
    noise_files = collect_files(NOISE_DIR)

    print(f"Found {len(positive_files)} positive files")
    print(f"Found {len(negative_files)} negative files")
    print(f"Found {len(noise_files)} noise files")

    noise_pool = [load_audio(p) for p in noise_files]

    x = []
    y = []

    print("\nProcessing positive samples...")
    for path in positive_files:
        audio = load_audio(path)
        variants = [
            fix_length(audio),
            random_gain(fix_length(audio)),
            time_shift(fix_length(audio)),
            add_noise(fix_length(audio), noise_pool, 0.02),
        ]
        for item in variants:
            x.append(extract_features(item))
            y.append(1)

    print(f"Processing negative samples...")
    for path in negative_files:
        audio = load_audio(path)
        variants = [
            fix_length(audio),
            random_gain(fix_length(audio)),
            time_shift(fix_length(audio)),
            add_noise(fix_length(audio), noise_pool, 0.03),
        ]
        for item in variants:
            x.append(extract_features(item))
            y.append(0)

    x = np.array(x, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    return x, y


def create_model_no_reshape(input_shape=(49, 40, 1), num_classes=2):
    """
    创建完全避免 SHAPE 算子的模型

    关键：在 Input 层指定 batch_size=1，让 TensorFlow 在编译时知道确切形状
    """
    model = keras.Sequential([
        # 关键：指定 batch_size=1
        layers.Input(shape=input_shape, batch_size=1),

        # 第一个卷积块
        layers.Conv2D(8, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),  # (1, 24, 20, 8)

        # 第二个卷积块
        layers.Conv2D(16, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),  # (1, 12, 10, 16)

        # 第三个卷积块
        layers.Conv2D(32, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),  # (1, 6, 5, 32)

        # 第四个卷积块
        layers.Conv2D(64, (3, 3), padding="same", activation="relu"),
        layers.MaxPooling2D((2, 2)),  # (1, 3, 2, 64)

        # 使用 Conv2D 降到 1x1
        layers.Conv2D(64, (3, 2), padding="valid", activation="relu"),  # (1, 1, 1, 64)

        # 使用 1x1 卷积代替 Dense
        layers.Conv2D(32, (1, 1), activation="relu"),  # (1, 1, 1, 32)
        layers.Conv2D(num_classes, (1, 1), activation=None),  # (1, 1, 1, 2)

        # Reshape 到 (1, 2) - 因为 batch_size=1，不会引入 SHAPE 算子
        layers.Reshape((num_classes,)),  # (1, 2)

        # Softmax
        layers.Softmax(),
    ])
    return model


def export_tflite(model, output_path):
    """导出为纯 float32 TFLite"""
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # 不使用任何优化
    tflite_model = converter.convert()
    with open(output_path, "wb") as f:
        f.write(tflite_model)


def main():
    print("="*60)
    print("Wake Word Model Training (No SHAPE Operator)")
    print("="*60)

    x, y = build_dataset()
    print(f"\nDataset x: {x.shape} {x.dtype}")
    print(f"Dataset y: {y.shape} {y.dtype}")
    print(f"Positive samples: {np.sum(y == 1)}")
    print(f"Negative samples: {np.sum(y == 0)}")

    x_train, x_temp, y_train, y_temp = train_test_split(
        x, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_temp, y_temp, test_size=0.5, random_state=RANDOM_SEED, stratify=y_temp
    )

    print(f"\nTrain set: {len(x_train)}")
    print(f"Val set: {len(x_val)}")
    print(f"Test set: {len(x_test)}")

    model = create_model_no_reshape()
    model.summary()

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            MODEL_DIR / "best_model.keras",
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
    ]

    print("\nStarting training...")
    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=30,
        batch_size=32,
        callbacks=callbacks,
        verbose=1,
    )

    print("\nEvaluating on test set...")
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"Test loss: {test_loss:.4f}")
    print(f"Test accuracy: {test_acc:.4f}")

    model.save(MODEL_DIR / "final_model.keras")
    np.save(MODEL_DIR / "history.npy", history.history)

    print("\nExporting to TFLite...")
    export_tflite(model, MODEL_DIR / "model.tflite")
    print(f"Model exported to: {MODEL_DIR / 'model.tflite'}")

    print("\n" + "="*60)
    print("Training completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python verify_tflite_ops.py models/no_shape_wake_word/model.tflite")
    print("2. If passed, run: python convert_to_c.py models/no_shape_wake_word/model.tflite")


if __name__ == "__main__":
    main()
