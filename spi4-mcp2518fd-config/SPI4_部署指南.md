# NanoPi M5 SPI4 + MCP2518FD 部署指南

## 当前状态

已完成：
- ✅ 设备树文件创建 (spi4-mcp2518fd.dts)
- ✅ 设备树编译 (spi4-mcp2518fd.dtbo)
- ✅ 参数确认 (40MHz 晶振, GPIO4_A5 中断)

## 问题

FriendlyElec 系统不支持标准的 /boot/overlays 目录，也不支持通过 configfs 动态加载设备树覆盖。

## 解决方案

### 方案1: 复制到 /lib/firmware 并尝试加载

```bash
sudo cp spi4-mcp2518fd.dtbo /lib/firmware/
./load_spi4_overlay.sh
```

### 方案2: 查找 FriendlyElec 官方方法

查看 FriendlyElec 文档了解如何修改设备树和启用 SPI。

### 方案3: 直接修改主设备树

需要找到并修改主设备树源文件，然后重新编译。

## 已创建的文件

- spi4-mcp2518fd.dts
- spi4-mcp2518fd.dtbo
- load_spi4_overlay.sh
- SPI4_最终配置.md

## 下一步

1. 尝试运行 load_spi4_overlay.sh
2. 如果失败，查看 FriendlyElec 官方文档
