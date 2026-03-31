/*
 * wake_word_detector.cc
 * 语音唤醒词检测器实现
 */

#include "wake_word_detector.h"
#include "model_data.h"
#include "audio_processing.h"

#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include <stdio.h>

// TensorFlow Lite Micro 内存分配
constexpr int kTensorArenaSize = 60 * 1024;  // 60KB
alignas(16) uint8_t tensor_arena[kTensorArenaSize];

// 全局变量
namespace {
const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;
}  // namespace

// 初始化检测器
bool WakeWordDetector_Init(void) {
    // 初始化 TensorFlow Lite
    tflite::InitializeTarget();

    // 加载模型
    model = tflite::GetModel(wake_word_model);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        printf("ERROR: Model schema version mismatch!\n");
        printf("Expected: %d, Got: %d\n",
               TFLITE_SCHEMA_VERSION, model->version());
        return false;
    }

    // 注册需要的操作
    static tflite::MicroMutableOpResolver<10> micro_op_resolver;

    if (micro_op_resolver.AddConv2D() != kTfLiteOk) return false;
    if (micro_op_resolver.AddMaxPool2D() != kTfLiteOk) return false;
    if (micro_op_resolver.AddReshape() != kTfLiteOk) return false;
    if (micro_op_resolver.AddFullyConnected() != kTfLiteOk) return false;
    if (micro_op_resolver.AddSoftmax() != kTfLiteOk) return false;
    if (micro_op_resolver.AddMean() != kTfLiteOk) return false;
    if (micro_op_resolver.AddPad() != kTfLiteOk) return false;
    if (micro_op_resolver.AddRelu() != kTfLiteOk) return false;

    // 创建解释器
    static tflite::MicroInterpreter static_interpreter(
        model, micro_op_resolver, tensor_arena, kTensorArenaSize);
    interpreter = &static_interpreter;

    // 分配张量
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        printf("ERROR: AllocateTensors() failed\n");
        return false;
    }

    // 获取输入输出张量
    input = interpreter->input(0);
    output = interpreter->output(0);

    // 验证输入输出维度
    if (input->dims->size != 4) {
        printf("ERROR: Expected 4D input tensor\n");
        return false;
    }

    printf("Wake Word Detector initialized successfully!\n");
    printf("Model size: %d bytes\n", wake_word_model_len);
    printf("Input shape: [%d, %d, %d, %d]\n",
           input->dims->data[0], input->dims->data[1],
           input->dims->data[2], input->dims->data[3]);
    printf("Arena used: %d / %d bytes (%.1f%%)\n",
           interpreter->arena_used_bytes(), kTensorArenaSize,
           100.0f * interpreter->arena_used_bytes() / kTensorArenaSize);

    return true;
}

// 运行唤醒词检测
bool WakeWordDetector_Detect(const int16_t* audio_data, int audio_len, float* confidence) {
    if (interpreter == nullptr || input == nullptr || output == nullptr) {
        printf("ERROR: Detector not initialized\n");
        return false;
    }

    // 提取 MFCC 特征
    float mfcc_features[INPUT_SIZE];
    if (!AudioProcessing_ExtractMFCC(audio_data, audio_len, mfcc_features, N_FRAMES, N_MFCC)) {
        printf("ERROR: MFCC extraction failed\n");
        return false;
    }

    // 将特征复制到输入张量
    for (int i = 0; i < INPUT_SIZE; i++) {
        input->data.f[i] = mfcc_features[i];
    }

    // 运行推理
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        printf("ERROR: Invoke failed\n");
        return false;
    }

    // 获取输出 (softmax 输出: [background, wake_word])
    float background_score = output->data.f[0];
    float wake_word_score = output->data.f[1];

    *confidence = wake_word_score;

    // 判断是否为唤醒词
    return wake_word_score > WAKE_WORD_THRESHOLD;
}

// 获取模型信息
void WakeWordDetector_GetInfo(void) {
    printf("\n=== Wake Word Detector Info ===\n");
    printf("Model: Marvin Wake Word\n");
    printf("Sample Rate: %d Hz\n", SAMPLE_RATE);
    printf("Audio Duration: %d ms\n", AUDIO_DURATION_MS);
    printf("MFCC Features: %d\n", N_MFCC);
    printf("Time Frames: %d\n", N_FRAMES);
    printf("Detection Threshold: %.2f\n", WAKE_WORD_THRESHOLD);
    printf("Model Size: %d bytes (%.2f KB)\n",
           wake_word_model_len, wake_word_model_len / 1024.0f);

    if (interpreter != nullptr) {
        printf("Arena Used: %d bytes (%.2f KB)\n",
               interpreter->arena_used_bytes(),
               interpreter->arena_used_bytes() / 1024.0f);
    }
    printf("===============================\n\n");
}
