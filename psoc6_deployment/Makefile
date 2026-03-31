# Makefile for PSoC 6 Wake Word Detection
# 需要根据实际的 ModusToolbox 项目调整

################################################################################
# 基本配置
################################################################################

# 应用名称
APPNAME=wake_word_detection

# 工具链
TOOLCHAIN=GCC_ARM

# 目标板
TARGET=CY8CKIT-062S2-43012

# 构建配置
CONFIG=Debug

################################################################################
# 源文件
################################################################################

# C/C++ 源文件
SOURCES=\
	main.cc \
	wake_word_detector.cc \
	audio_processing.cc

# 头文件目录
INCLUDES=\
	-I. \
	-I$(TFLM_PATH) \
	-I$(TFLM_PATH)/third_party/flatbuffers/include \
	-I$(TFLM_PATH)/third_party/gemmlowp \
	-I$(TFLM_PATH)/third_party/ruy

################################################################################
# TensorFlow Lite Micro
################################################################################

TFLM_PATH=../libs/tensorflow-lite-micro

# TFLite Micro 源文件
TFLM_SOURCES=\
	$(wildcard $(TFLM_PATH)/tensorflow/lite/micro/*.cc) \
	$(wildcard $(TFLM_PATH)/tensorflow/lite/micro/kernels/*.cc) \
	$(wildcard $(TFLM_PATH)/tensorflow/lite/micro/memory_planner/*.cc) \
	$(wildcard $(TFLM_PATH)/tensorflow/lite/core/api/*.cc) \
	$(wildcard $(TFLM_PATH)/tensorflow/lite/kernels/internal/*.cc) \
	$(wildcard $(TFLM_PATH)/tensorflow/lite/kernels/*.cc)

# 排除不需要的文件
TFLM_SOURCES:=$(filter-out %test.cc %_test.cc, $(TFLM_SOURCES))

SOURCES+=$(TFLM_SOURCES)

################################################################################
# 编译选项
################################################################################

# C++ 标准
CXXFLAGS+=-std=c++11

# TFLite Micro 定义
DEFINES+=\
	-DTF_LITE_STATIC_MEMORY \
	-DTF_LITE_DISABLE_X86_NEON \
	-DNDEBUG

# 优化选项
ifeq ($(CONFIG),Release)
CXXFLAGS+=-O3 -flto
else
CXXFLAGS+=-O0 -g
endif

# ARM Cortex-M4 选项
CXXFLAGS+=\
	-mcpu=cortex-m4 \
	-mthumb \
	-mfloat-abi=softfp \
	-mfpu=fpv4-sp-d16

# 警告选项
CXXFLAGS+=\
	-Wall \
	-Wno-unused-parameter \
	-Wno-sign-compare

################################################################################
# 可选：ARM CMSIS-DSP
################################################################################

# 如果使用 CMSIS-DSP，取消注释以下行
# DEFINES+=-DUSE_CMSIS_DSP
# INCLUDES+=-I$(CMSIS_PATH)/CMSIS/DSP/Include
# SOURCES+=$(CMSIS_PATH)/CMSIS/DSP/Source/**/*.c

################################################################################
# 链接选项
################################################################################

LDFLAGS+=\
	-Wl,--gc-sections \
	-Wl,--print-memory-usage

################################################################################
# 构建规则
################################################################################

.PHONY: all clean build program

all: build

build:
	@echo "Building $(APPNAME)..."
	@echo "Sources: $(SOURCES)"
	# 实际构建命令需要使用 ModusToolbox 的 make 系统
	# make -C .. build

clean:
	@echo "Cleaning..."
	# make -C .. clean

program:
	@echo "Programming..."
	# make -C .. program

################################################################################
# 帮助
################################################################################

help:
	@echo "PSoC 6 Wake Word Detection Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all      - Build the application (default)"
	@echo "  build    - Build the application"
	@echo "  clean    - Clean build artifacts"
	@echo "  program  - Program the device"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Configuration:"
	@echo "  CONFIG=Debug|Release"
	@echo ""
	@echo "Note: This Makefile is a template."
	@echo "      Integrate with ModusToolbox build system for actual builds."
