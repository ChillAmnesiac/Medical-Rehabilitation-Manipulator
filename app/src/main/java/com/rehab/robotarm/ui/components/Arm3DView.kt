package com.rehab.robotarm.ui.components

import android.content.Context
import android.view.MotionEvent
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import org.rajawali3d.Object3D
import org.rajawali3d.lights.DirectionalLight
import org.rajawali3d.materials.Material
import org.rajawali3d.materials.methods.DiffuseMethod
import org.rajawali3d.math.vector.Vector3
import org.rajawali3d.primitives.Cylinder
import org.rajawali3d.primitives.Sphere
import org.rajawali3d.renderer.Renderer
import org.rajawali3d.view.SurfaceView

/**
 * 3D手臂视图组件
 * 显示机械臂的实时运动状态
 */
@Composable
fun Arm3DView(
    shoulderAngle: Float,      // 肩关节纵向角度
    elbowAngle: Float,         // 肘关节纵向角度
    lateralAngle: Float,       // 肩关节横向张开角度
    modifier: Modifier = Modifier
) {
    var renderer: ArmRenderer? by remember { mutableStateOf(null) }

    AndroidView(
        modifier = modifier,
        factory = { context ->
            val surfaceView = SurfaceView(context)
            val newRenderer = ArmRenderer(context)
            renderer = newRenderer
            surfaceView.setSurfaceRenderer(newRenderer)
            surfaceView.setFrameRate(60.0)

            surfaceView
        },
        update = { _ ->
            renderer?.updateArmAngles(shoulderAngle, elbowAngle, lateralAngle)
        }
    )
}

/**
 * 手臂3D渲染器
 */
class ArmRenderer(context: Context) : Renderer(context) {

    private lateinit var shoulderJoint: Object3D
    private lateinit var upperArm: Object3D
    private lateinit var elbowJoint: Object3D
    private lateinit var forearm: Object3D
    private lateinit var hand: Object3D

    private var sceneInitialized = false
    private var currentShoulderAngle = 0f
    private var currentElbowAngle = 0f
    private var currentLateralAngle = 0f

    private var lastX = 0f
    private var lastY = 0f
    private var cameraDistance = 12f
    private var cameraRotationX = 15f
    private var cameraRotationY = 30f

    override fun initScene() {
        // 设置相机
        updateCamera()

        // 主光源（从上方照射）
        val mainLight = DirectionalLight(0.3, -1.0, 0.5)
        mainLight.setColor(1.0f, 1.0f, 1.0f)
        mainLight.power = 1.5f
        currentScene.addLight(mainLight)

        // 补光（从侧面）
        val fillLight = DirectionalLight(-1.0, 0.0, 0.5)
        fillLight.setColor(1.0f, 1.0f, 1.0f)
        fillLight.power = 0.8f
        currentScene.addLight(fillLight)

        // 环境光
        val ambientLight = DirectionalLight(0.0, 1.0, 0.0)
        ambientLight.setColor(1.0f, 0.98f, 0.95f)
        ambientLight.power = 0.6f
        currentScene.addLight(ambientLight)

        // 皮肤材质 - 更真实的肤色
        val skinMaterial = Material().apply {
            enableLighting(true)
            diffuseMethod = DiffuseMethod.Lambert()
            setColor(0xffF4C2A0.toInt())
        }

        // 关节材质 - 稍微深一点
        val jointMaterial = Material().apply {
            enableLighting(true)
            diffuseMethod = DiffuseMethod.Lambert()
            setColor(0xffE8B090.toInt())
        }

        // 手部材质 - 稍浅
        val handMaterial = Material().apply {
            enableLighting(true)
            diffuseMethod = DiffuseMethod.Lambert()
            setColor(0xffF8D0B0.toInt())
        }

        // ===== 肩部结构 =====
        shoulderJoint = Sphere(0.7f, 48, 48).apply {
            material = jointMaterial
            position = Vector3(0.0, 0.0, 0.0)
        }
        currentScene.addChild(shoulderJoint)

        // 肩部连接
        val shoulderConnector = Cylinder(0.6f, 0.8f, 48, 48).apply {
            material = skinMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 0.4, 0.0)
        }
        shoulderJoint.addChild(shoulderConnector)

        // ===== 上臂 =====
        val upperArmTop = Cylinder(0.55f, 2.0f, 48, 48).apply {
            material = skinMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 1.8, 0.0)
        }
        shoulderJoint.addChild(upperArmTop)

        val upperArmMid = Cylinder(0.5f, 1.5f, 48, 48).apply {
            material = skinMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 3.55, 0.0)
        }
        shoulderJoint.addChild(upperArmMid)

        upperArm = Cylinder(0.45f, 1.2f, 48, 48).apply {
            material = skinMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 4.9, 0.0)
        }
        shoulderJoint.addChild(upperArm)

        // ===== 肘关节 =====
        elbowJoint = Sphere(0.5f, 48, 48).apply {
            material = jointMaterial
            position = Vector3(0.0, 5.5, 0.0)
        }
        shoulderJoint.addChild(elbowJoint)

        val elbowTip = Sphere(0.35f, 32, 32).apply {
            material = jointMaterial
            position = Vector3(0.0, 0.0, -0.4)
        }
        elbowJoint.addChild(elbowTip)

        // ===== 前臂 =====
        val forearmTop = Cylinder(0.42f, 1.8f, 48, 48).apply {
            material = skinMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 0.9, 0.0)
        }
        elbowJoint.addChild(forearmTop)

        val forearmMid = Cylinder(0.38f, 1.5f, 48, 48).apply {
            material = skinMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 2.55, 0.0)
        }
        elbowJoint.addChild(forearmMid)

        forearm = Cylinder(0.32f, 1.2f, 48, 48).apply {
            material = skinMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 3.9, 0.0)
        }
        elbowJoint.addChild(forearm)

        // ===== 手腕 =====
        val wrist = Sphere(0.35f, 32, 32).apply {
            material = jointMaterial
            position = Vector3(0.0, 4.5, 0.0)
            scale = Vector3(1.0, 0.8, 0.9)
        }
        elbowJoint.addChild(wrist)

        // ===== 手掌 =====
        val palm = Cylinder(0.4f, 1.2f, 32, 32).apply {
            material = handMaterial
            rotate(Vector3.Axis.Z, 90.0)
            position = Vector3(0.0, 5.1, 0.0)
            scale = Vector3(1.0, 1.0, 0.6)
        }
        elbowJoint.addChild(palm)

        // ===== 手指 =====
        hand = Sphere(0.5f, 32, 32).apply {
            material = handMaterial
            position = Vector3(0.0, 5.7, 0.0)
            scale = Vector3(1.3, 0.7, 0.5)
        }
        elbowJoint.addChild(hand)

        sceneInitialized = true

        // 应用初始角度
        updateArmAngles(currentShoulderAngle, currentElbowAngle, currentLateralAngle)
    }

    /**
     * 更新手臂角度
     */
    fun updateArmAngles(shoulderAngle: Float, elbowAngle: Float, lateralAngle: Float) {
        currentShoulderAngle = shoulderAngle
        currentElbowAngle = elbowAngle
        currentLateralAngle = lateralAngle

        if (!sceneInitialized) return

        // 应用旋转
        shoulderJoint.setRotation(
            lateralAngle.toDouble(),
            0.0,
            -shoulderAngle.toDouble()
        )

        elbowJoint.setRotZ(-elbowAngle.toDouble())
    }

    /**
     * 更新相机位置
     */
    private fun updateCamera() {
        val radX = Math.toRadians(cameraRotationX.toDouble())
        val radY = Math.toRadians(cameraRotationY.toDouble())

        val x = cameraDistance * Math.sin(radY) * Math.cos(radX)
        val y = cameraDistance * Math.sin(radX)
        val z = cameraDistance * Math.cos(radY) * Math.cos(radX)

        currentCamera.setPosition(x, y, z)
        currentCamera.setLookAt(0.0, 3.0, 0.0)
    }

    override fun onOffsetsChanged(
        xOffset: Float,
        yOffset: Float,
        xOffsetStep: Float,
        yOffsetStep: Float,
        xPixelOffset: Int,
        yPixelOffset: Int
    ) {
    }

    override fun onTouchEvent(event: MotionEvent?) {
        if (event == null) return

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
            }
            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY

                cameraRotationY += dx * 0.5f
                cameraRotationX += dy * 0.5f

                cameraRotationX = cameraRotationX.coerceIn(-89f, 89f)

                updateCamera()

                lastX = event.x
                lastY = event.y
            }
        }
    }
}
