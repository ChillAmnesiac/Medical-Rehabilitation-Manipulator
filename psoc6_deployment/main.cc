/*
 * main.cc
 * PSoC 6 Edge E84 Talk - 语音唤醒词检测主程序
 */

#include "wake_word_detector.h"
#include "audio_processing.h"
#include <stdio.h>

// PSoC 6 HAL (根据实际使用的库调整)
// #include "cyhal.h"
// #include "cybsp.h"
// #include "cyhal_pdm_pcm.h"

// 音频缓冲区
static int16_t audio_buffer[SAMPLE_RATE];  // 1秒音频 @ 16kHz

// 麦克风初始化 (示例代码，需要根据实际硬件调整)
bool init_microphone(void) {
    // TODO: 初始化 PDM 麦克风
    /*
    cyhal_pdm_pcm_t pdm_pcm;
    cyhal_pdm_pcm_cfg_t pdm_pcm_cfg = {
        .sample_rate = SAMPLE_RATE,
        .decimation_rate = 64,
        .mode = CYHAL_PDM_PCM_MODE_LEFT,
        .word_length = 16,
        .left_gain = 0,
        .right_gain = 0,
    };

    cy_rslt_t result = cyhal_pdm_pcm_init(&pdm_pcm, PDM_DATA, PDM_CLK,
                                          &audio_clock, &pdm_pcm_cfg);
    if (result != CY_RSLT_SUCCESS) {
        printf("ERROR: PDM PCM init failed\n");
        return false;
    }
    */

    printf("Microphone initialized (placeholder)\n");
    return true;
}

// 从麦克风读取音频
bool get_audio_from_mic(int16_t* buffer, int length) {
    // TODO: 从麦克风读取音频数据
    /*
    size_t read_length = length;
    cy_rslt_t result = cyhal_pdm_pcm_read(&pdm_pcm, buffer, &read_length);
    if (result != CY_RSLT_SUCCESS) {
        printf("ERROR: Audio read failed\n");
        return false;
    }
    */

    // 占位符：生成测试数据
    for (int i = 0; i < length; i++) {
        buffer[i] = 0;  // 静音
    }

    return true;
}

// 主函数
int main(void) {
    // 初始化系统
    printf("\n");
    printf("========================================\n");
    printf("  PSoC 6 Wake Word Detection System\n");
    printf("========================================\n");

    // 初始化音频处理
    if (!AudioProcessing_Init()) {
        printf("ERROR: Audio processing init failed\n");
        return -1;
    }

    // 初始化唤醒词检测器
    if (!WakeWordDetector_Init()) {
        printf("ERROR: Wake word detector init failed\n");
        return -1;
    }

    // 显示模型信息
    WakeWordDetector_GetInfo();

    // 初始化麦克风
    if (!init_microphone()) {
        printf("ERROR: Microphone init failed\n");
        return -1;
    }

    printf("System ready. Listening for wake word...\n\n");

    // 主循环
    int detection_count = 0;
    while (1) {
        // 从麦克风获取音频数据
        if (!get_audio_from_mic(audio_buffer, SAMPLE_RATE)) {
            printf("ERROR: Failed to get audio\n");
            continue;
        }

        // 检测唤醒词
        float confidence = 0.0f;
        bool is_wake_word = WakeWordDetector_Detect(audio_buffer, SAMPLE_RATE, &confidence);

        if (is_wake_word) {
            detection_count++;
            printf("[%d] *** WAKE WORD DETECTED! *** Confidence: %.2f%%\n",
                   detection_count, confidence * 100.0f);

            // TODO: 触发后续动作
            // - 点亮 LED
            // - 播放提示音
            // - 启动语音识别
            // - 发送通知等

            // 防止重复触发，延时一段时间
            // cyhal_system_delay_ms(1000);
        } else {
            // 可选：显示置信度（调试用）
            // printf("Confidence: %.2f%%\r", confidence * 100.0f);
        }

        // 延时或等待下一帧音频
        // cyhal_system_delay_ms(100);
    }

    return 0;
}
