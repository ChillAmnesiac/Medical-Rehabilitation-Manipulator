"""
基于官方 microfrontend 参数的数据处理器
符合 TensorFlow Lite Micro micro_speech 示例的特征提取
"""
import numpy as np
import librosa

class MicrofrontendProcessor:
    """
    模拟官方 microfrontend 的特征提取
    参数来自 micro_speech 示例
    """

    def __init__(self):
        # 音频参数
        self.sample_rate = 16000
        self.duration = 1.0  # 1秒

        # 官方 microfrontend 参数
        self.window_size_ms = 30  # 30ms 窗长
        self.window_stride_ms = 20  # 20ms 步长
        self.n_features = 40  # 40 维特征
        self.n_frames = 49  # 49 帧

        # FFT 参数
        self.n_fft = 512

        # 计算帧参数
        self.window_size_samples = int(self.sample_rate * self.window_size_ms / 1000)
        self.hop_length = int(self.sample_rate * self.window_stride_ms / 1000)

        # Mel 滤波器参数（官方参数）
        self.fmin = 125.0  # lower band limit
        self.fmax = 7500.0  # upper band limit

        print(f"Microfrontend Processor 初始化:")
        print(f"  采样率: {self.sample_rate} Hz")
        print(f"  窗长: {self.window_size_ms} ms ({self.window_size_samples} samples)")
        print(f"  步长: {self.window_stride_ms} ms ({self.hop_length} samples)")
        print(f"  特征维度: {self.n_features}")
        print(f"  帧数: {self.n_frames}")
        print(f"  输入形状: ({self.n_frames}, {self.n_features}, 1)")

    def load_audio(self, file_path):
        """加载音频文件"""
        audio, sr = librosa.load(file_path, sr=self.sample_rate, duration=self.duration)

        # 填充或截断到固定长度
        target_length = int(self.sample_rate * self.duration)
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]

        return audio

    def extract_features(self, audio):
        """
        提取特征，尽量接近官方 microfrontend

        官方流程:
        1. 分帧加窗
        2. FFT
        3. Mel 滤波器组
        4. 对数缩放
        5. PCAN (可选)
        """
        # 使用 librosa 提取 Mel 频谱图
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.window_size_samples,
            n_mels=self.n_features,
            fmin=self.fmin,
            fmax=self.fmax,
            power=2.0  # 功率谱
        )

        # 转换为对数刻度（dB）
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # 转置为 (时间, 特征) 格式
        features = mel_spec_db.T

        # 确保帧数为 49
        if features.shape[0] < self.n_frames:
            # 填充
            pad_width = self.n_frames - features.shape[0]
            features = np.pad(features, ((0, pad_width), (0, 0)), mode='constant')
        elif features.shape[0] > self.n_frames:
            # 截断
            features = features[:self.n_frames, :]

        # 归一化
        features = (features - np.mean(features)) / (np.std(features) + 1e-10)

        return features

    def process_audio_file(self, file_path):
        """处理单个音频文件"""
        audio = self.load_audio(file_path)
        features = self.extract_features(audio)
        return features

    def load_dataset(self, wake_word_dir, background_dir):
        """
        加载数据集

        返回:
            X: 特征数组 [N, 49, 40]
            y: 标签数组 [N]
        """
        import os

        X = []
        y = []

        # 加载唤醒词样本
        print("\n加载唤醒词样本...")
        if os.path.exists(wake_word_dir):
            files = [f for f in os.listdir(wake_word_dir) if f.endswith(('.wav', '.mp3', '.flac'))]
            for file in files:
                file_path = os.path.join(wake_word_dir, file)
                try:
                    features = self.process_audio_file(file_path)
                    X.append(features)
                    y.append(1)  # 唤醒词标签
                except Exception as e:
                    print(f"  处理文件 {file} 时出错: {e}")
            print(f"  加载了 {len([i for i in y if i == 1])} 个唤醒词样本")

        # 加载背景音样本
        print("加载背景音样本...")
        if os.path.exists(background_dir):
            files = [f for f in os.listdir(background_dir) if f.endswith(('.wav', '.mp3', '.flac'))]
            for file in files:
                file_path = os.path.join(background_dir, file)
                try:
                    features = self.process_audio_file(file_path)
                    X.append(features)
                    y.append(0)  # 背景音标签
                except Exception as e:
                    print(f"  处理文件 {file} 时出错: {e}")
            print(f"  加载了 {len([i for i in y if i == 0])} 个背景音样本")

        X = np.array(X)
        y = np.array(y)

        # 添加通道维度 [N, 49, 40] -> [N, 49, 40, 1]
        X = np.expand_dims(X, -1)

        print(f"\n数据集加载完成:")
        print(f"  总样本数: {len(X)}")
        print(f"  唤醒词样本: {np.sum(y == 1)}")
        print(f"  背景音样本: {np.sum(y == 0)}")
        print(f"  特征形状: {X.shape}")

        return X, y


if __name__ == "__main__":
    # 测试
    processor = MicrofrontendProcessor()
    print("\n特征提取器初始化完成")
