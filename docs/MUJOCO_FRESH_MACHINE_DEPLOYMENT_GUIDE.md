# MuJoCo 工程盘点与新电脑从零部署指南

本文用于把康复外骨骼机械臂的 MuJoCo/ROS 2 仿真环境部署到一台全新的电脑，并说明 GitHub 仓库与 `cal` 仿真主机之间目前存在的资产差异。

> 审计日期：2026-07-19  
> MuJoCo/ROS 2 主线：`feature/rehab-arm-ros2-architecture`  
> 审计提交：`69450f7165e608f99fc4b574beffa5ac50d2331f`  
> 推荐系统：Ubuntu 24.04 Desktop + ROS 2 Jazzy

## 1. 结论

当前 GitHub 仓库可以复现“简化版 ROS 2 + MuJoCo 6DOF shadow”，但不能仅靠仓库完整还原 `cal` 主机上带真实 CAD、STL 网格和专用启动脚本的可视化工程。

需要特别注意：

1. 仓库默认代码不在 `main`，MuJoCo/ROS 2 工程位于 `feature/rehab-arm-ros2-architecture` 分支。
2. 仓库里的 URDF 和 MJCF 都是简化模型；`cal` 上记录的真实 URDF、STL 和完整 MJCF 尚未进入 Git。
3. 当前 ROS 2 MuJoCo 节点没有集成交互式 viewer，也没有 RViz 完整启动链路。
4. 当前 MuJoCo backend 是关节位置 shadow：它直接更新 `qpos/qvel` 并调用 `mj_forward()`，没有调用 `mj_step()`，不能当作完整动力学仿真。
5. 当前仓库没有锁定 MuJoCo Python 版本，也没有 Dockerfile 或一键安装脚本。

## 2. 仓库里已经有什么

MuJoCo/ROS 2 主线仓库：

```text
https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator.git
branch: feature/rehab-arm-ros2-architecture
```

关键内容如下。

| 类型 | 路径 | 说明 |
|---|---|---|
| 简化 URDF | `rehab_arm_ros2_ws/src/rehab_arm_description/urdf/rehab_arm.urdf` | 5 个关节，使用 box/cylinder 等基础几何体 |
| 5DOF MJCF | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/models/rehab_arm_minimal.xml` | 早期 5 关节基线 |
| 6DOF MJCF | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/models/medical_arm_6dof.xml` | 6 关节简化 shadow 模型 |
| MuJoCo backend | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/rehab_arm_sim_mujoco/mujoco_backend.py` | 模型加载、限位夹紧和关节状态更新 |
| ROS 2 仿真节点 | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/rehab_arm_sim_mujoco/mujoco_sim_node.py` | 接收 `JointTrajectory`，发布 `JointState` |
| 硬件 shadow relay | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/rehab_arm_sim_mujoco/medical_arm_shadow_relay_node.py` | NanoPi/真机状态到仿真关节的映射 |
| 环境自检 | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/rehab_arm_sim_mujoco/check_sim_env.py` | 检查 ROS、MuJoCo、模型和 launch 文件 |
| 单机 launch | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/launch/medical_arm_6dof_shadow.launch.py` | 启动 6DOF shadow |
| 硬件 shadow launch | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/launch/medical_arm_6dof_hardware_shadow.launch.py` | 只读跟随 NanoPi `/joint_states` |
| 关节配置 | `rehab_arm_ros2_ws/src/rehab_arm_description/config/medical_arm_6dof_schema.yaml` | 6DOF 名称、限位和电机映射草案 |
| 测试 | `rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/test/` | backend、自检、shadow relay 和架构合同测试 |

审计时重新运行了 `test_mujoco_backend.py`，10 个测试全部通过。这些测试主要验证模型文件、关节名、关节范围和限位夹紧，不代表 ROS 2、图形界面或真实动力学已经在全新 Ubuntu 上完成集成验证。

## 3. `cal` 主机记录了什么

仓库文档记录，2026-06-02 在以下位置建立过完整可视化目录：

```text
cal@192.168.2.46:/home/cal/medical_arm_mujoco/
```

记录中的文件包括：

```text
/home/cal/medical_arm_mujoco/
  medical_arm_mujoco.xml
  medical_arm_viewer.urdf
  urdf/medical_arm.urdf
  meshes/*.STL
  README_MUJOCO.md
  joint_motor_mapping.yaml
  validate_mujoco.py
  open_mujoco.sh
  medical_arm_mujoco_preview.png
  medical_arm_mujoco_preview_close.png
```

这些文件目前没有被 Git 跟踪：

- `medical_arm_mujoco.xml`
- `medical_arm_viewer.urdf`
- `urdf/medical_arm.urdf`
- `meshes/*.STL`
- `README_MUJOCO.md`
- `joint_motor_mapping.yaml`
- `validate_mujoco.py`
- `open_mujoco.sh`
- MuJoCo 预览图

审计时 `192.168.2.46:22` 可以建立 TCP 连接，但远端在 SSH 密钥交换前主动关闭连接。因此上述内容来自仓库内的历史记录，不能视为 2026-07-19 对 `cal` 实时文件和未提交改动的确认。

## 4. 当前已知缺口

### 4.1 模型资产缺口

- 仓库没有真实机械臂 STL 网格。
- 仓库没有 `cal` 上的完整 6DOF CAD URDF。
- 仓库没有 cleaned Xacro。
- 仓库内 5DOF URDF 与 6DOF MJCF 的关节合同尚未完全统一。
- 真实关节方向、零点、传动比、回差和电机映射仍有未标定项。

### 4.2 运行链路缺口

- `rehab_arm_description/launch/description.launch.py` 目前只声明 `use_sim_time`，没有启动 `robot_state_publisher`、joint state publisher 或 RViz。
- 部分 README 提到 `rehab_arm_bringup sim.launch.py` 和 `real_nanopi.launch.py`，但这两个文件不在仓库中。
- `mujoco` 没有写入 `package.xml` 或可复现的 Python 依赖文件，必须手工安装。
- MuJoCo ROS 节点是无界面的；启动 ROS 节点不会自动打开 MuJoCo viewer。
- 当前 backend 没有执行 `mj_step()`，属于位置 shadow，不是完整动力学闭环。

## 5. 新电脑从零部署现有简化版

### 5.1 选择操作系统

推荐安装原生 Ubuntu 24.04 Desktop。

第一版不建议使用 Windows/WSL，原因是后续还会涉及：

- ROS 2 DDS 局域网发现；
- MuJoCo/OpenGL 图形显示；
- SocketCAN；
- NanoPi 与仿真主机之间的无线 ROS 2 通信。

项目当前脚本显式支持 ROS 2 Jazzy 和 Humble。Ubuntu 24.04 对应 ROS 2 Jazzy，最符合现有仓库文档和构建脚本。

### 5.2 推荐版本与兼容性基线

原 `cal` 仿真环境的仓库记录是：

```text
Ubuntu 24.04
ROS 2 Jazzy
Python 3.12
Python mujoco 3.9.0
独立 MuJoCo simulate viewer 3.10
```

这套组合本身不存在版本冲突：

- ROS 2 Jazzy 官方支持 Ubuntu 24.04。
- Ubuntu 24.04 默认 Python 3.12。
- `mujoco 3.9.0` 要求 Python 3.10 或更高，并提供 Python 3.12 wheel。
- Python `mujoco 3.9.0` 自带对应版本的 MuJoCo 动态库；独立 `simulate 3.10` 使用自己的运行库，两者不在同一进程中，可以同时存在。
- 仓库代码只调用 `MjModel.from_xml_string()`、`MjData`、`mj_name2id()` 和 `mj_forward()` 等基础 API，没有使用与 ROS 2 Jazzy 绑定的 MuJoCo 扩展接口。

推荐组合如下：

| Ubuntu | ROS 2 | Python | MuJoCo | 用途与结论 |
|---|---|---|---|---|
| 24.04 | Jazzy | 3.12 | `3.9.0` | 首次完整复现，推荐基线 |
| 24.04 | Jazzy | 3.12 | `3.10.0` | 升级验证组合，不作为首次部署基线 |
| 22.04 | Humble | 3.10 | 兼容版本 | 可以单独适配，但不是原验证环境 |
| 22.04 | Jazzy | 系统默认 | 任意 | 不推荐，ROS deb 与系统版本不匹配 |
| 24.04 | Humble | 系统默认 | 任意 | 不推荐，ROS deb 与系统版本不匹配 |

MuJoCo Python 包和 ROS 2 在本项目中是松耦合的。最容易导致部署失败的不是 Jazzy 与 MuJoCo 版本号，而是：

1. `pip` 把 MuJoCo 安装到了另一个 Python。
2. 普通 venv 看不到 ROS 2 的系统 `rclpy`。
3. 新电脑执行未锁版本的 `pip install mujoco`，安装了未经本项目验证的新版。
4. 无界面 EGL 配置被拿来启动桌面 viewer。
5. 安装了旧的 `mujoco-py`，而不是官方 `mujoco` 包。

官方版本信息：

```text
ROS 2 Jazzy Ubuntu: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
MuJoCo 3.9.0:       https://pypi.org/project/mujoco/3.9.0/
MuJoCo 当前版本:    https://pypi.org/project/mujoco/
```

### 5.3 安装 ROS 2 Jazzy

以下命令参考 ROS 2 Jazzy 官方 Ubuntu deb 安装流程：

```bash
sudo apt update
sudo apt install -y locales software-properties-common curl git python3-venv

sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

sudo add-apt-repository universe

export ROS_APT_SOURCE_VERSION=$(
  curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest |
  grep -F '"tag_name"' | awk -F'"' '{print $4}'
)

curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
sudo apt install -y ros-jazzy-desktop ros-dev-tools
```

加载 ROS 环境并初始化 `rosdep`：

```bash
source /opt/ros/jazzy/setup.bash
sudo rosdep init
rosdep update
```

如果 `sudo rosdep init` 只提示已经初始化，则跳过这一条，继续执行 `rosdep update`。

验证 ROS 2：

```bash
source /opt/ros/jazzy/setup.bash
ros2 --help
```

官方安装文档：

```text
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
```

### 5.4 克隆正确分支

不要直接使用默认分支。执行：

```bash
mkdir -p ~/robot
cd ~/robot

git clone --single-branch \
  --branch feature/rehab-arm-ros2-architecture \
  https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator.git

cd Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws
```

确认分支：

```bash
git branch --show-current
```

预期输出：

```text
feature/rehab-arm-ros2-architecture
```

### 5.5 创建 Python 环境并安装 MuJoCo

创建能够访问系统 ROS Python 包的虚拟环境：

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws

source /opt/ros/jazzy/setup.bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install "mujoco==3.9.0"
```

官方 MuJoCo Python 包已经包含 MuJoCo 运行库，不需要另外下载旧版 `mujoco-py` 或手工安装 MuJoCo SDK。

验证 MuJoCo：

```bash
python -c "import mujoco; print(mujoco.__version__)"
```

首次复现的预期输出是：

```text
3.9.0
```

确认 Python、ROS 2 和 MuJoCo 位于同一运行环境：

```bash
source /opt/ros/jazzy/setup.bash
source .venv/bin/activate

which python
python --version
python -m pip show mujoco

python - <<'PY'
import sys
import rclpy
import mujoco

print("python:", sys.executable)
print("rclpy:", rclpy.__file__)
print("mujoco:", mujoco.__version__)
print("mujoco module:", mujoco.__file__)
PY
```

预期条件：

- Python 是工作区 `.venv/bin/python`。
- Python 版本为 3.12.x。
- `rclpy` 能正常导入。
- `mujoco` 版本为 3.9.0。

如果虚拟环境内提示 `No module named rclpy`，删除并重新创建 venv：

```bash
deactivate 2>/dev/null || true
rm -rf .venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "mujoco==3.9.0"
```

不要用裸 `pip` 判断安装位置，统一使用：

```bash
python -m pip ...
```

如果需要验证 MuJoCo 3.10.0，使用另一个虚拟环境，不要覆盖已验证的 3.9.0 环境：

```bash
python3 -m venv --system-site-packages .venv-mujoco310
source .venv-mujoco310/bin/activate
python -m pip install --upgrade pip
python -m pip install "mujoco==3.10.0"
python -c "import mujoco; print(mujoco.__version__)"
```

官方 Python 安装说明：

```text
https://mujoco.readthedocs.io/en/stable/python.html#installation
```

### 5.6 安装 ROS 包依赖

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate

rosdep install \
  --from-paths src \
  --ignore-src \
  --rosdistro jazzy \
  -r -y
```

通过标准：

```text
#All required rosdeps installed successfully
```

### 5.7 编译 MuJoCo 相关包

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate

bash ./build_ros2.sh \
  --packages-select \
  rehab_arm_description \
  rehab_arm_sim_mujoco

source install/setup.bash
```

确认 ROS 2 能找到包：

```bash
ros2 pkg prefix rehab_arm_sim_mujoco
ros2 pkg executables rehab_arm_sim_mujoco
```

### 5.8 运行严格环境自检

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate
source install/setup.bash

ros2 run rehab_arm_sim_mujoco \
  check_sim_env.py --strict-mujoco --pretty
```

通过标准：

```text
readiness=ready_with_mujoco
checks.mujoco.ok=true
errors=[]
```

如果显示 `ready_with_fallback_sim`，说明 ROS topic 合同可以运行，但当前 Python 环境没有真正加载官方 MuJoCo 包。

### 5.9 启动 6DOF MuJoCo shadow

终端 A：

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate
source install/setup.bash

ros2 launch rehab_arm_sim_mujoco \
  medical_arm_6dof_shadow.launch.py
```

日志应包含：

```text
backend=mujoco-model
```

如果显示 `fallback-first-order`，说明启动成功但没有进入 MuJoCo backend。

终端 B：

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws

source /opt/ros/jazzy/setup.bash
source .venv/bin/activate
source install/setup.bash

ros2 topic echo --once \
  /sim/medical_arm/joint_states \
  sensor_msgs/msg/JointState
```

检查发布频率：

```bash
ros2 topic hz /sim/medical_arm/joint_states
```

### 5.10 EGL 与桌面 viewer

当前 ROS 2 节点不会打开图形界面。可以单独查看仓库内的简化 MJCF：

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws
source .venv/bin/activate
unset MUJOCO_GL

python -m mujoco.viewer \
  --mjcf="$PWD/src/rehab_arm_sim_mujoco/models/medical_arm_6dof.xml"
```

这个 viewer 只加载模型文件，不会自动跟随 ROS 2 `/sim/medical_arm/joint_states`。

图形后端按场景区分：

| 场景 | 配置 |
|---|---|
| 无显示器服务器、离屏验证 | `export MUJOCO_GL=egl` |
| Ubuntu 桌面交互 viewer | `unset MUJOCO_GL` |

如果桌面 viewer 报 GLFW、DISPLAY 或窗口无法创建，先检查：

```bash
echo "$DISPLAY"
echo "${MUJOCO_GL:-not_set}"
unset MUJOCO_GL
python -m mujoco.viewer \
  --mjcf="$PWD/src/rehab_arm_sim_mujoco/models/medical_arm_6dof.xml"
```

`MUJOCO_GL=egl` 适用于 headless/offscreen 场景，不应写死为所有终端的桌面 viewer 默认值。

### 5.11 每个新终端都要加载环境

每次打开新终端，至少执行：

```bash
cd ~/robot/Medical-Rehabilitation-Manipulator/rehab_arm_ros2_ws
source /opt/ros/jazzy/setup.bash
source .venv/bin/activate
source install/setup.bash
```

## 6. 接入 NanoPi 前的网络配置

仿真主机和 NanoPi 必须：

- 位于可互通的局域网；
- 使用相同 `ROS_DOMAIN_ID`；
- 允许 DDS 组播或显式配置 DDS peers；
- 首次联调保持 NanoPi `enable_target_tx=false`。

示例：

```bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
```

先做只读检查：

```bash
ros2 topic list
ros2 topic echo /joint_states
ros2 topic echo /rehab_arm/safety_state
```

不要在网络发现、关节映射、反馈新鲜度或安全状态不明确时发送真机轨迹。

## 7. 完整迁移 `cal` 工程

仅完成第 5 节只能运行仓库内的简化模型。要完整迁移 `cal`，必须先恢复 SSH 或在 `cal` 本机操作。

### 7.1 在 `cal` 本机检查 SSH

```bash
sudo systemctl status ssh
sudo journalctl -u ssh -n 100 --no-pager
sudo ss -ltnp | grep ':22'
```

需要解决“TCP 已建立，但 SSH 密钥交换前连接被关闭”的问题后，才能确认远端实时文件。

### 7.2 归档并生成校验值

在 `cal` 上执行：

```bash
cd /home/cal

tar -czf medical_arm_mujoco-cal-backup.tar.gz \
  medical_arm_mujoco

sha256sum medical_arm_mujoco-cal-backup.tar.gz \
  > medical_arm_mujoco-cal-backup.tar.gz.sha256
```

复制到新电脑后验证：

```bash
sha256sum -c medical_arm_mujoco-cal-backup.tar.gz.sha256
tar -xzf medical_arm_mujoco-cal-backup.tar.gz
```

### 7.3 正式纳入 Git 仓库

建议目标结构：

```text
rehab_arm_ros2_ws/src/rehab_arm_description/
  urdf/
    medical_arm_raw.urdf
    rehab_arm.urdf.xacro
  meshes/
    visual/*.STL
    collision/
  config/
    joint_mapping.yaml
    joint_limits.yaml

rehab_arm_ros2_ws/src/rehab_arm_sim_mujoco/
  models/
    medical_arm_mujoco.xml
  scripts/
    validate_mujoco.py
    open_mujoco.sh
```

STL 较大时使用 Git LFS：

```bash
sudo apt install -y git-lfs
git lfs install
git lfs track '*.STL'
git add .gitattributes
```

在提交前必须确认：

- MJCF 对 STL 的相对路径在安装后仍然有效；
- `CMakeLists.txt` 会安装 `models/`、`meshes/` 和必要脚本；
- 不包含患者数据、密钥、token 或主机私有配置；
- 每个关节的方向、零点、传动比和标定状态都有明确来源；
- 未确认的映射写为 `null` 或 `unverified`，不能猜成正式参数。

### 7.4 固化软件依赖

为了让下一台电脑真正可复现，应补充至少一份依赖锁定文件，例如：

```text
requirements-sim.txt
```

首次基线至少应固定：

```text
mujoco==3.9.0
```

MuJoCo 3.10.0 应先在独立虚拟环境完成 XML 加载、backend 合同测试、ROS 自检和 viewer 验证，再决定是否更新基线。

内容应以 `cal` 实际验证环境为准，并记录：

- Python 版本；
- `mujoco` 版本；
- Ubuntu 版本；
- ROS 2 发行版；
- GPU/mesa/NVIDIA 驱动版本；
- viewer 启动方式；
- headless 时使用的 `MUJOCO_GL` 设置。

## 8. 部署验收清单

### 8.1 仓库与环境

- [ ] 当前分支是 `feature/rehab-arm-ros2-architecture`。
- [ ] `source /opt/ros/jazzy/setup.bash` 无错误。
- [ ] Python 版本是 3.12.x。
- [ ] `python -c "import rclpy, mujoco"` 成功。
- [ ] 首次复现使用 `mujoco==3.9.0`。
- [ ] `python -m pip show mujoco` 与 ROS 节点实际 Python 是同一环境。
- [ ] `rosdep install` 无未解决依赖。
- [ ] `colcon build` 成功。
- [ ] `check_sim_env.py --strict-mujoco` 返回 `ready_with_mujoco`。

### 8.2 简化仿真

- [ ] 启动日志显示 `backend=mujoco-model`。
- [ ] `/sim/medical_arm/joint_states` 有 6 个关节。
- [ ] 关节名与 `medical_arm_6dof_schema.yaml` 一致。
- [ ] `ros2 topic hz /sim/medical_arm/joint_states` 稳定。
- [ ] 超范围目标会被限位夹紧。

### 8.3 完整 `cal` 迁移

- [ ] 真实 URDF 已进入 Git。
- [ ] 所有 STL 已进入 Git 或 Git LFS。
- [ ] 完整 MJCF 可以在新电脑加载。
- [ ] `validate_mujoco.py` 在新电脑通过。
- [ ] viewer 能显示正确外观、关节轴和末端位置。
- [ ] 所有资产路径不再依赖 `/home/cal/...` 绝对路径。
- [ ] 依赖版本和系统信息已经锁定。

### 8.4 NanoPi 只读 shadow

- [ ] 仿真主机能够发现 NanoPi ROS 2 topic。
- [ ] `ROS_DOMAIN_ID` 和 DDS 配置一致。
- [ ] `enable_target_tx=false`。
- [ ] CAN 抓包确认没有发送 `0x320` 目标帧。
- [ ] MuJoCo 只跟随状态，不参与急停、限流或实时安全裁决。

## 9. 安全边界

本项目是穿戴式医疗康复外骨骼，部署仿真环境不能改变以下原则：

- MuJoCo、ROS 2、NanoPi、服务器和 VLA 都不是最终安全权威；
- 真机运动必须经过 M33 安全状态机；
- 急停、限位、限速、限流和通信超时必须在 M33 本地独立有效；
- 无线 ROS 2 适合状态同步、规划、回放、数据采集和 dry-run，不适合急停或高频电流/力矩闭环；
- 新轨迹必须依次经过离线仿真、dry-run、空载小角度台架验证，才能讨论穿戴测试；
- 关节映射、零点、方向或反馈新鲜度不明确时，默认不允许运动。

## 10. 最终判断

当前可执行目标分为两级：

1. **仓库可复现目标**：在全新 Ubuntu 24.04 上运行简化 6DOF MuJoCo shadow，并通过 ROS 2 topic 验证。
2. **完整工程目标**：从 `cal` 恢复真实 URDF、STL、完整 MJCF 和配套脚本，将其正式纳入 Git 并锁定依赖后，才能在任意新电脑完整复现原可视化工程。

在第二级完成前，不应把当前仓库描述为“已经完整包含 `cal` MuJoCo 工程”。
