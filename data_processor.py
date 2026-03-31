import os
import numpy as np
import librosa
import tensorflow as tf
from sklearn.model_selection import train_test_split

class AudioDataProcessor:
    """音频数据处理器"""

    def __init__(self, sample_rate=16000, duration=1.0, n_mfcc=40):
        """
        初始化音频处理器

        参数:
            sample_rate: 采样率 (Hz)
            duration: 音频时长 (秒)
            n_mfcc: MFCC特征数量
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.n_mfcc = n_mfcc
        self.samples = int(sample_rate * duration)

    def load_audio(self, file_path):
        """加载音频文件"""
        audio, sr = librosa.load(file_path, sr=self.sample_rate, duration=self.duration)

        # 填充或截断到固定长度
        if len(audio) < self.samples:
            audio = np.pad(audio, (0, self.samples - len(audio)))
        else:
            audio = audio[:self.samples]

        return audio

    def extract_mfcc(self, audio):
        """提取MFCC特征"""
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=self.sample_rate,
            n_mfcc=self.n_mfcc,
            n_fft=512,
            hop_length=160
        )
        return mfcc.T  # 转置为 (时间步, 特征数)

    def process_audio_file(self, file_path):
        """处理单个音频文件"""
        audio = self.load_audio(file_path)
        mfcc = self.extract_mfcc(audio)
        return mfcc

    def load_dataset(self, wake_word_dir, background_dir):
        """
        加载数据集

        参数:
            wake_word_dir: 唤醒词音频目录
            background_dir: 背景音/非唤醒词音频目录

        返回:
            X: 特征数组
            y: 标签数组
        """
        X = []
        y = []

        # 加载唤醒词样本
        print("加载唤醒词样本...")
        if os.path.exists(wake_word_dir):
            for file in os.listdir(wake_word_dir):
                if file.endswith(('.wav', '.mp3', '.flac')):
                    file_path = os.path.join(wake_word_dir, file)
                    try:
                        mfcc = self.process_audio_file(file_path)
                        X.append(mfcc)
                        y.append(1)  # 唤醒词标签
                    except Exception as e:
                        print(f"处理文件 {file} 时出错: {e}")

        # 加载背景音样本
        print("加载背景音样本...")
        if os.path.exists(background_dir):
            for file in os.listdir(background_dir):
                if file.endswith(('.wav', '.mp3', '.flac')):
                    file_path = os.path.join(background_dir, file)
                    try:
                        mfcc = self.process_audio_file(file_path)
                        X.append(mfcc)
                        y.append(0)  # 非唤醒词标签
                    except Exception as e:
                        print(f"处理文件 {file} 时出错: {e}")

        X = np.array(X)
        y = np.array(y)

        # 添加通道维度
        X = np.expand_dims(X, -1)

        print(f"数据集加载完成: {len(X)} 个样本")
        print(f"唤醒词样本: {np.sum(y == 1)}")
        print(f"背景音样本: {np.sum(y == 0)}")

        return X, y

    def augment_audio(self, audio):
        """数据增强"""
        # 随机添加噪声
        if np.random.random() < 0.5:
            noise = np.random.randn(len(audio)) * 0.005
            audio = audio + noise

        # 随机改变音量
        if np.random.random() < 0.5:
            audio = audio * np.random.uniform(0.7, 1.3)

        # 随机时间偏移
        if np.random.random() < 0.5:
            shift = np.random.randint(-1600, 1600)
            audio = np.roll(audio, shift)

        return audio


def prepare_dataset(wake_word_dir, background_dir, test_size=0.2, val_size=0.1):
    """
    准备训练、验证和测试数据集

    参数:
        wake_word_dir: 唤醒词目录
        background_dir: 背景音目录
        test_size: 测试集比例
        val_size: 验证集比例

    返回:
        (X_train, y_train), (X_val, y_val), (X_test, y_test)
    """
    processor = AudioDataProcessor()
    X, y = processor.load_dataset(wake_word_dir, background_dir)

    # 分割数据集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=val_size, random_state=42, stratify=y_train
    )

    print(f"\n训练集: {len(X_train)} 样本")
    print(f"验证集: {len(X_val)} 样本")
    print(f"测试集: {len(X_test)} 样本")

    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


if __name__ == "__main__":
    # 测试数据处理
    processor = AudioDataProcessor()
    print(f"采样率: {processor.sample_rate} Hz")
    print(f"音频时长: {processor.duration} 秒")
    print(f"MFCC特征数: {processor.n_mfcc}")
