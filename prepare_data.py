import os
import shutil
import random

def prepare_wake_word_dataset(
    raw_data_dir="/home/cal/wake_word_model/data/raw",
    wake_word="marvin",  # 可选: marvin, sheila, yes, no 等
    output_wake_dir="/home/cal/wake_word_model/data/wake_word",
    output_bg_dir="/home/cal/wake_word_model/data/background",
    num_wake_samples=500,
    num_bg_samples=1000
):
    """
    从 Google Speech Commands 数据集准备训练数据

    参数:
        raw_data_dir: 原始数据目录
        wake_word: 唤醒词（数据集中的词）
        output_wake_dir: 唤醒词输出目录
        output_bg_dir: 背景音输出目录
        num_wake_samples: 唤醒词样本数量
        num_bg_samples: 背景音样本数量
    """

    print("="*60)
    print("准备训练数据集")
    print("="*60)

    # 清空输出目录
    os.makedirs(output_wake_dir, exist_ok=True)
    os.makedirs(output_bg_dir, exist_ok=True)

    # 复制唤醒词样本
    wake_word_dir = os.path.join(raw_data_dir, wake_word)
    if os.path.exists(wake_word_dir):
        files = [f for f in os.listdir(wake_word_dir) if f.endswith('.wav')]
        random.shuffle(files)
        files = files[:num_wake_samples]

        print(f"\n复制 {len(files)} 个唤醒词样本 ('{wake_word}')...")
        for i, file in enumerate(files):
            src = os.path.join(wake_word_dir, file)
            dst = os.path.join(output_wake_dir, f"wake_{i:04d}.wav")
            shutil.copy(src, dst)
        print(f"✓ 唤醒词样本: {len(files)}")
    else:
        print(f"错误: 找不到唤醒词目录 {wake_word_dir}")
        return

    # 复制背景音样本（使用其他词作为负样本）
    background_words = ["zero", "one", "two", "three", "four", "five",
                       "six", "seven", "eight", "nine", "up", "down",
                       "left", "right", "on", "off", "stop", "go"]

    # 排除唤醒词
    if wake_word in background_words:
        background_words.remove(wake_word)

    print(f"\n复制背景音样本...")
    bg_count = 0
    samples_per_word = num_bg_samples // len(background_words) + 1

    for word in background_words:
        word_dir = os.path.join(raw_data_dir, word)
        if os.path.exists(word_dir):
            files = [f for f in os.listdir(word_dir) if f.endswith('.wav')]
            random.shuffle(files)
            files = files[:samples_per_word]

            for file in files:
                if bg_count >= num_bg_samples:
                    break
                src = os.path.join(word_dir, file)
                dst = os.path.join(output_bg_dir, f"bg_{bg_count:04d}.wav")
                shutil.copy(src, dst)
                bg_count += 1

        if bg_count >= num_bg_samples:
            break

    print(f"✓ 背景音样本: {bg_count}")

    # 添加真实背景噪音
    noise_dir = os.path.join(raw_data_dir, "_background_noise_")
    if os.path.exists(noise_dir):
        noise_files = [f for f in os.listdir(noise_dir) if f.endswith('.wav')]
        print(f"\n找到 {len(noise_files)} 个背景噪音文件")
        for file in noise_files:
            src = os.path.join(noise_dir, file)
            dst = os.path.join(output_bg_dir, f"noise_{file}")
            shutil.copy(src, dst)
            bg_count += 1

    print("\n" + "="*60)
    print("数据准备完成！")
    print(f"唤醒词样本: {output_wake_dir}")
    print(f"背景音样本: {output_bg_dir}")
    print("="*60)


if __name__ == "__main__":
    # 准备数据集
    # 可以选择不同的唤醒词: marvin, sheila, yes, no 等
    prepare_wake_word_dataset(
        wake_word="marvin",
        num_wake_samples=500,
        num_bg_samples=1000
    )
