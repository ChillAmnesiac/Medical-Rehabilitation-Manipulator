const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// 存储最新的数据
const latestData = {
  image: null,
  audio: null,
  motors: [],
  sensors: []
};

// 客户端类型
const clients = {
  ros: null,      // ROS客户端
  vla: null,      // VLA客户端
  web: new Set()  // Web监控客户端
};

app.use(express.static('public'));

wss.on('connection', (ws, req) => {
  console.log('New connection from:', req.socket.remoteAddress);

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);

      // 处理客户端注册
      if (data.type === 'register') {
        if (data.role === 'ros') {
          clients.ros = ws;
          console.log('ROS client registered');
          ws.send(JSON.stringify({ type: 'registered', role: 'ros' }));
        } else if (data.role === 'vla') {
          clients.vla = ws;
          console.log('VLA client registered');
          ws.send(JSON.stringify({ type: 'registered', role: 'vla' }));
        } else if (data.role === 'web') {
          clients.web.add(ws);
          console.log('Web client registered');
          // 发送最新数据给新连接的web客户端
          ws.send(JSON.stringify({
            type: 'initial_data',
            data: latestData
          }));
        }
      }

      // 处理ROS发来的数据
      else if (data.type === 'ros_data') {
        if (data.dataType === 'image') {
          latestData.image = data.payload;
        } else if (data.dataType === 'audio') {
          latestData.audio = data.payload;
        } else if (data.dataType === 'motors') {
          latestData.motors = data.payload;
        } else if (data.dataType === 'sensors') {
          latestData.sensors = data.payload;
        }

        // 广播给所有web客户端
        const broadcastData = JSON.stringify({
          type: 'ros_data',
          dataType: data.dataType,
          payload: data.payload,
          timestamp: Date.now()
        });

        clients.web.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(broadcastData);
          }
        });
      }

      // 处理VLA发来的指令
      else if (data.type === 'vla_command') {
        if (clients.ros && clients.ros.readyState === WebSocket.OPEN) {
          clients.ros.send(JSON.stringify({
            type: 'vla_command',
            command: data.command,
            timestamp: Date.now()
          }));
          console.log('Command sent to ROS:', data.command);
        }

        // 同时广播给web客户端显示
        const broadcastData = JSON.stringify({
          type: 'vla_command',
          command: data.command,
          timestamp: Date.now()
        });

        clients.web.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(broadcastData);
          }
        });
      }

    } catch (error) {
      console.error('Error processing message:', error);
    }
  });

  ws.on('close', () => {
    // 清理断开的客户端
    if (clients.ros === ws) {
      clients.ros = null;
      console.log('ROS client disconnected');
    } else if (clients.vla === ws) {
      clients.vla = null;
      console.log('VLA client disconnected');
    } else if (clients.web.has(ws)) {
      clients.web.delete(ws);
      console.log('Web client disconnected');
    }
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`WebSocket server running on port ${PORT}`);
  console.log(`Web interface: http://localhost:${PORT}`);
});
