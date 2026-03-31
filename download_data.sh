#!/bin/bash
# 下载 Google Speech Commands 数据集

cd /home/cal/wake_word_model/data/raw

echo "下载 Google Speech Commands 数据集..."
wget -c http://download.tensorflow.org/data/speech_commands_v0.02.tar.gz

echo "解压数据集..."
tar -xzf speech_commands_v0.02.tar.gz

echo "数据集下载完成！"
