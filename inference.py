import numpy as np
import librosa
import tensorflow as tf
from data_processor import AudioDataProcessor

class WakeWordDetector:
    """语音唤醒词检测器"""

    def __init__(self, model_path, threshold=0.8):
        """
        初始化检测器

        参数:
            model_path: 模型文件路径 (.keras 或 .tflite)
            threshold: 检测阈值 (0-1)
        """
        self.threshold = threshold
        self.processor = AudioDataProcessor()

        # 加载模型
        if model_path.endswith('.tflite'):
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.use_tflite = True
        else:
            self.model = tf.keras.models.load_model(model_path)
            self.use_tflite = False

        print(f"模型加载成功: {model_path}")
        print(f"检测阈值: {threshold}")

    def predict(self, audio_path):
        """
        预测音频是否包含唤醒词

        参数:
            audio_path: 音频文件路径

        返回:
            is_wake_word: 是否为唤醒词 (bool)
            confidence: 置信度 (float)
        """
        # 处理音频
        mfcc = self.processor.process_audio_file(audio_path)
        mfcc = np.expand_dims(mfcc, axis=0)  # 添加批次维度
        mfcc = np.expand_dims(mfcc, axis=-1)  # 添加通道维度

        # 预测
        if self.use_tflite:
            self.interpreter.set_tensor(self.input_details[0]['index'], mfcc.astype(np.float32))
            self.interpreter.invoke()
            predictions = self.interpreter.get_tensor(self.output_details[0]['index'])
        else:
            predictions = self.model.predict(mfcc, verbose=0)

        confidence = predictions[0][1]  # 唤醒词类别的置信度
        is_wake_word = confidence >= self.threshold

        return is_wake_word, confidence

    def predict_stream(self, audio_data):
        """
        实时流式预测

        参数:
            audio_data: 音频数据 (numpy array)

        返回:
            is_wake_word: 是否为唤醒词
            confidence: 置信度
        """
        # 提取特征
        mfcc = self.processor.extract_mfcc(audio_data)
        mfcc = np.expand_dims(mfcc, axis=0)
        mfcc = np.expand_dims(mfcc, axis=-1)

        # 预测
        if self.use_tflite:
            self.interpreter.set_tensor(self.input_details[0]['index'], mfcc.astype(np.float32))
            self.interpreter.invoke()
            predictions = self.interpreter.get_tensor(self.output_details[0]['index'])
        else:
            predictions = self.model.predict(mfcc, verbose=0)

        confidence = predictions[0][1]
        is_wake_word = confidence >= self.threshold

        return is_wake_word, confidence


def test_model(model_path, test_audio_dir, threshold=0.8):
    """
    测试模型

    参数:
        model_path: 模型路径
        test_audio_dir: 测试音频目录
        threshold: 检测阈值
    """
    import os

    detector = WakeWordDetector(model_path, threshold)

    print("\n开始测试...")
    print("="*60)

    if not os.path.exists(test_audio_dir):
        print(f"测试目录不存在: {test_audio_dir}")
        return

    for file in os.listdir(test_audio_dir):
        if file.endswith(('.wav', '.mp3', '.flac')):
            file_path = os.path.join(test_audio_dir, file)
            try:
                is_wake_word, confidence = detector.predict(file_path)
                status = "✓ 唤醒词" if is_wake_word else "✗ 非唤醒词"
                print(f"{file:30s} | {status} | 置信度: {confidence:.4f}")
            except Exception as e:
                print(f"{file:30s} | 错误: {e}")

    print("="*60)


if __name__ == "__main__":
    # 示例：测试模型
    model_path = "./models/wake_word_standard_20240101_120000/best_model.keras"
    test_audio_dir = "./data/test"

    test_model(model_path, test_audio_dir, threshold=0.8)
