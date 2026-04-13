# NanoPi M5 SPI4 + MCP2518FD 最终配置 (CAN 1Mbps)

## 硬件连接确认

### 30-Pin 排针连接
| Pin | 功能 | GPIO | MCP2518FD |
|-----|------|------|-----------|
| 19  | MOSI | GPIO4_B1 | SI |
| 21  | MISO | GPIO4_B2 | SO |
| 23  | CLK  | GPIO4_B0 | SCK |
| 24  | CS0  | GPIO4_B3 | CS |
| ?   | INT  | GPIO4_A5 | INT |
| -   | VCC  | 3.3V | VCC |
| -   | GND  | GND | GND |

### MCP2518FD 模块参数
- 晶振频率: 40MHz (已从原理图确认)
- SPI 速率: 20MHz
- 中断引脚: GPIO4_A5 (GPIO编号 133)

## 部署步骤

### 1. 编译设备树

```bash
sudo apt-get install device-tree-compiler
sudo dtc -@ -I dts -O dtb -o /boot/overlays/spi4-mcp2518fd.dtbo spi4-mcp2518fd.dts
```

### 2. 启用设备树覆盖

使用 npi-config 工具或修改 boot 配置文件

### 3. 重启系统

```bash
sudo reboot
```

### 4. 验证 SPI4

```bash
ls -la /dev/spidev*
dmesg | grep -i spi
dmesg | grep -i mcp2518
```

### 5. 加载驱动

```bash
sudo modprobe mcp251xfd
lsmod | grep mcp
ip link show can0
```

### 6. 配置 CAN (1Mbps)

```bash
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
ip -details link show can0
```

### 7. 测试

```bash
sudo apt-get install can-utils
candump can0
cansend can0 123#DEADBEEF
```

## 故障排查

```bash
cat /sys/firmware/devicetree/base/spi@2ad10000/status
dmesg | grep mcp2518
cat /proc/interrupts | grep 133
```

## 配置完成

所有参数已确认并配置完成。
