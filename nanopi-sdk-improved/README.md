# NanoPi M5 SPI4 + MCP2518FD CAN SDK

基于 FriendlyARM 官方 SDK 的完整配置方案

## 快速开始

```bash
cd scripts
chmod +x *.sh
./compile-overlay.sh
sudo ./install-overlay.sh
sudo reboot
sudo ./setup-can.sh 1000000
```

## 硬件连接

| Pin | 功能 | MCP2518FD |
|-----|------|-----------|
| 19 | MOSI | SI |
| 21 | MISO | SO |
| 23 | CLK | SCK |
| 24 | CS0 | CS |
| 22 | INT | INT |
