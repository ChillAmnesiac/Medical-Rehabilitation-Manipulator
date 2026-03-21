package com.rehab.robotarm.data.export

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import com.itextpdf.kernel.colors.ColorConstants
import com.itextpdf.kernel.colors.DeviceRgb
import com.itextpdf.kernel.pdf.PdfDocument
import com.itextpdf.kernel.pdf.PdfWriter
import com.itextpdf.layout.Document
import com.itextpdf.layout.element.Cell
import com.itextpdf.layout.element.Image
import com.itextpdf.layout.element.Paragraph
import com.itextpdf.layout.element.Table
import com.itextpdf.layout.properties.TextAlignment
import com.itextpdf.layout.properties.UnitValue
import com.itextpdf.io.image.ImageDataFactory
import com.rehab.robotarm.data.database.entity.Patient
import com.rehab.robotarm.data.database.entity.RehabAssessment
import com.rehab.robotarm.data.database.entity.TrainingSession
import java.io.ByteArrayOutputStream
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class PdfExporter(private val context: Context) {

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
    private val dateOnlyFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

    /**
     * 生成康复评估报告PDF
     */
    suspend fun generateRehabReport(
        patient: Patient,
        sessions: List<TrainingSession>,
        assessments: List<RehabAssessment>,
        outputFile: File
    ): Result<File> {
        return try {
            val pdfWriter = PdfWriter(outputFile)
            val pdfDocument = PdfDocument(pdfWriter)
            val document = Document(pdfDocument)

            // 标题
            document.add(
                Paragraph("康复训练评估报告")
                    .setFontSize(24f)
                    .setBold()
                    .setTextAlignment(TextAlignment.CENTER)
                    .setMarginBottom(20f)
            )

            // 患者信息
            addPatientInfo(document, patient)

            // 训练统计
            addTrainingStatistics(document, sessions)

            // 康复评估详情
            addAssessmentDetails(document, assessments)

            // 评分趋势图
            if (assessments.isNotEmpty()) {
                addScoreTrendChart(document, assessments)
            }

            // 建议与总结
            addRecommendations(document, assessments)

            document.close()
            Result.success(outputFile)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun addPatientInfo(document: Document, patient: Patient) {
        document.add(
            Paragraph("患者信息")
                .setFontSize(18f)
                .setBold()
                .setMarginTop(10f)
        )

        val table = Table(UnitValue.createPercentArray(floatArrayOf(30f, 70f)))
            .useAllAvailableWidth()

        table.addCell(createCell("姓名"))
        table.addCell(createCell(patient.name))

        table.addCell(createCell("年龄"))
        table.addCell(createCell("${patient.age}岁"))

        table.addCell(createCell("性别"))
        table.addCell(createCell(patient.gender))

        table.addCell(createCell("诊断"))
        table.addCell(createCell(patient.diagnosis))

        table.addCell(createCell("患侧"))
        table.addCell(createCell(patient.affectedSide))

        table.addCell(createCell("入院日期"))
        table.addCell(createCell(dateOnlyFormat.format(Date(patient.admissionDate))))

        document.add(table)
    }

    private fun addTrainingStatistics(document: Document, sessions: List<TrainingSession>) {
        document.add(
            Paragraph("训练统计")
                .setFontSize(18f)
                .setBold()
                .setMarginTop(20f)
        )

        val totalSessions = sessions.size
        val totalDuration = sessions.sumOf { it.duration } / 60 // 转换为分钟
        val avgDuration = if (totalSessions > 0) totalDuration / totalSessions else 0
        val maxAngle = sessions.maxOfOrNull { it.maxAngle } ?: 0f
        val avgHeartRate = sessions.mapNotNull { it.avgHeartRate }.average().toInt()

        val table = Table(UnitValue.createPercentArray(floatArrayOf(50f, 50f)))
            .useAllAvailableWidth()

        table.addCell(createCell("总训练次数"))
        table.addCell(createCell("$totalSessions 次"))

        table.addCell(createCell("总训练时长"))
        table.addCell(createCell("$totalDuration 分钟"))

        table.addCell(createCell("平均训练时长"))
        table.addCell(createCell("$avgDuration 分钟"))

        table.addCell(createCell("最大关节角度"))
        table.addCell(createCell("${maxAngle}°"))

        table.addCell(createCell("平均心率"))
        table.addCell(createCell("$avgHeartRate bpm"))

        document.add(table)
    }

    private fun addAssessmentDetails(document: Document, assessments: List<RehabAssessment>) {
        document.add(
            Paragraph("康复评估详情")
                .setFontSize(18f)
                .setBold()
                .setMarginTop(20f)
        )

        if (assessments.isEmpty()) {
            document.add(Paragraph("暂无评估数据"))
            return
        }

        val latestAssessment = assessments.first()
        val avgSmooth = assessments.map { it.smoothness }.average()
        val avgROM = assessments.map { it.rangeOfMotion }.average()
        val avgStrength = assessments.map { it.strength }.average()
        val avgOverall = assessments.map { it.overallScore }.average()

        val table = Table(UnitValue.createPercentArray(floatArrayOf(40f, 30f, 30f)))
            .useAllAvailableWidth()

        // 表头
        table.addHeaderCell(createHeaderCell("评估项目"))
        table.addHeaderCell(createHeaderCell("最新评分"))
        table.addHeaderCell(createHeaderCell("平均评分"))

        // 数据行
        table.addCell(createCell("运动平滑度"))
        table.addCell(createCell(String.format("%.1f", latestAssessment.smoothness)))
        table.addCell(createCell(String.format("%.1f", avgSmooth)))

        table.addCell(createCell("运动范围(ROM)"))
        table.addCell(createCell(String.format("%.1f", latestAssessment.rangeOfMotion)))
        table.addCell(createCell(String.format("%.1f", avgROM)))

        table.addCell(createCell("力量评分"))
        table.addCell(createCell(String.format("%.1f", latestAssessment.strength)))
        table.addCell(createCell(String.format("%.1f", avgStrength)))

        table.addCell(createCell("综合评分"))
        table.addCell(createCell(String.format("%.1f", latestAssessment.overallScore)))
        table.addCell(createCell(String.format("%.1f", avgOverall)))

        document.add(table)
    }

    private fun addScoreTrendChart(document: Document, assessments: List<RehabAssessment>) {
        document.add(
            Paragraph("评分趋势")
                .setFontSize(18f)
                .setBold()
                .setMarginTop(20f)
        )

        // 生成趋势图
        val chartBitmap = generateTrendChart(assessments)
        val stream = ByteArrayOutputStream()
        chartBitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
        val imageData = ImageDataFactory.create(stream.toByteArray())
        val image = Image(imageData)
        image.setWidth(UnitValue.createPercentValue(80f))
        document.add(image)
    }

    private fun generateTrendChart(assessments: List<RehabAssessment>): Bitmap {
        val width = 800
        val height = 400
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)

        // 背景
        canvas.drawColor(Color.WHITE)

        val paint = Paint().apply {
            isAntiAlias = true
            strokeWidth = 3f
        }

        val textPaint = Paint().apply {
            isAntiAlias = true
            textSize = 24f
            color = Color.BLACK
        }

        // 绘制坐标轴
        val padding = 60f
        val chartWidth = width - 2 * padding
        val chartHeight = height - 2 * padding

        paint.color = Color.GRAY
        canvas.drawLine(padding, height - padding, width - padding, height - padding, paint) // X轴
        canvas.drawLine(padding, padding, padding, height - padding, paint) // Y轴

        // 绘制数据点和线条
        if (assessments.size > 1) {
            val stepX = chartWidth / (assessments.size - 1)
            val points = assessments.mapIndexed { index, assessment ->
                val x = padding + index * stepX
                val y = height - padding - (assessment.overallScore / 100f * chartHeight)
                Pair(x, y)
            }

            // 绘制线条
            paint.color = Color.BLUE
            paint.style = Paint.Style.STROKE
            for (i in 0 until points.size - 1) {
                canvas.drawLine(points[i].first, points[i].second, points[i + 1].first, points[i + 1].second, paint)
            }

            // 绘制数据点
            paint.style = Paint.Style.FILL
            points.forEach { (x, y) ->
                canvas.drawCircle(x, y, 8f, paint)
            }
        }

        // 绘制Y轴刻度
        for (i in 0..5) {
            val y = height - padding - (i * 20f / 100f * chartHeight)
            canvas.drawText("${i * 20}", 10f, y + 8f, textPaint)
        }

        return bitmap
    }

    private fun addRecommendations(document: Document, assessments: List<RehabAssessment>) {
        document.add(
            Paragraph("康复建议")
                .setFontSize(18f)
                .setBold()
                .setMarginTop(20f)
        )

        if (assessments.isEmpty()) {
            document.add(Paragraph("暂无建议"))
            return
        }

        val latestAssessment = assessments.first()
        document.add(
            Paragraph(latestAssessment.recommendation)
                .setMarginTop(10f)
        )

        if (!latestAssessment.cloudRecommendation.isNullOrEmpty()) {
            document.add(
                Paragraph("云端AI建议：")
                    .setBold()
                    .setMarginTop(10f)
            )
            document.add(
                Paragraph(latestAssessment.cloudRecommendation)
                    .setMarginTop(5f)
            )
        }

        // 总结
        document.add(
            Paragraph("总结")
                .setFontSize(18f)
                .setBold()
                .setMarginTop(20f)
        )

        val avgScore = assessments.map { it.overallScore }.average()
        val trend = if (assessments.size >= 2) {
            val recent = assessments.take(3).map { it.overallScore }.average()
            val older = assessments.drop(3).take(3).map { it.overallScore }.average()
            when {
                recent > older + 5 -> "显著进步"
                recent > older -> "稳步提升"
                recent < older - 5 -> "需要关注"
                else -> "保持稳定"
            }
        } else {
            "数据不足"
        }

        document.add(
            Paragraph("患者平均评分为 ${String.format("%.1f", avgScore)} 分，康复进度呈现 $trend 趋势。建议继续按照训练计划进行康复训练，定期复查评估。")
                .setMarginTop(10f)
        )

        // 生成日期
        document.add(
            Paragraph("报告生成日期：${dateFormat.format(Date())}")
                .setTextAlignment(TextAlignment.RIGHT)
                .setMarginTop(30f)
                .setFontSize(10f)
                .setFontColor(ColorConstants.GRAY)
        )
    }

    private fun createCell(text: String): Cell {
        return Cell().add(Paragraph(text)).setPadding(5f)
    }

    private fun createHeaderCell(text: String): Cell {
        return Cell()
            .add(Paragraph(text).setBold())
            .setBackgroundColor(DeviceRgb(230, 230, 230))
            .setPadding(5f)
    }
}
