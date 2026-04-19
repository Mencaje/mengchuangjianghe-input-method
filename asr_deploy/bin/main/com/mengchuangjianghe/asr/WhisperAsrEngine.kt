package com.mengchuangjianghe.asr

import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.TimeUnit

/**
 * 纯本地语音识别引擎，基于 OpenAI Whisper 开源实现（如 whisper.cpp）进行调用与优化。
 * 不连接任何第三方接口，所有识别在本地完成。
 *
 * 使用方式：需本地已安装 whisper.cpp 或兼容的可执行程序，并指定模型文件路径。
 * 本引擎将 PCM 转为 WAV 后调用本地可执行程序，解析输出文本。
 *
 * 版权与协议：识别核心基于 OpenAI Whisper（MIT License），见项目 NOTICE 文件。
 */
class WhisperAsrEngine(
    private val modelPath: String,
    private val executablePath: String = "main",
    private val processTimeoutSeconds: Long = 60L
) : AsrEngine {

    private var available = modelPath.isNotBlank() && executablePath.isNotBlank()
    private val modelFile: File? = if (modelPath.isBlank()) null else File(modelPath)
    private val execFile: File? = if (executablePath.isBlank()) null else File(executablePath)

    override fun isAvailable(): Boolean = available &&
        (modelFile?.exists() == true) &&
        (execFile?.exists() == true || !executablePath.contains(File.separator))

    override fun recognize(pcmData: ByteArray, sampleRate: Int): AsrResult {
        if (!available || pcmData.isEmpty()) {
            return AsrResult(if (pcmData.isEmpty()) "" else "未配置模型或可执行路径", 0f, true)
        }
        var tempFile: File? = null
        return try {
            tempFile = File.createTempFile("whisper_", ".wav")
            writeWav16(tempFile, pcmData, sampleRate)
            val output = runWhisper(tempFile)
            val text = TextRefiner.refine(output)
            AsrResult(text, 0.9f, true)
        } catch (e: Exception) {
            AsrResult("本地识别异常: ${e.message}", 0f, true)
        } finally {
            tempFile?.delete()
        }
    }

    private fun writeWav16(file: File, pcmData: ByteArray, sampleRate: Int) {
        val dataLen = pcmData.size
        val totalLen = 36 + dataLen
        FileOutputStream(file).use { out ->
            out.write("RIFF".toByteArray(Charsets.US_ASCII))
            out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(totalLen).array())
            out.write("WAVE".toByteArray(Charsets.US_ASCII))
            out.write("fmt ".toByteArray(Charsets.US_ASCII))
            out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(16).array())
            out.write(ByteBuffer.allocate(2).order(ByteOrder.LITTLE_ENDIAN).putShort(1).array())
            out.write(ByteBuffer.allocate(2).order(ByteOrder.LITTLE_ENDIAN).putShort(1).array())
            out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(sampleRate).array())
            out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(sampleRate * 2).array())
            out.write(ByteBuffer.allocate(2).order(ByteOrder.LITTLE_ENDIAN).putShort(2).array())
            out.write(ByteBuffer.allocate(2).order(ByteOrder.LITTLE_ENDIAN).putShort(16).array())
            out.write("data".toByteArray(Charsets.US_ASCII))
            out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(dataLen).array())
            out.write(pcmData)
        }
    }

    private fun runWhisper(audioFile: File): String {
        val builder = ProcessBuilder(
            executablePath,
            "-m", modelPath,
            "-f", audioFile.absolutePath,
            "--no-timestamps",
            "-l", "auto"
        ).redirectErrorStream(true)
        val process = builder.start()
        val output = process.inputStream.bufferedReader(Charsets.UTF_8).readText()
        if (!process.waitFor(processTimeoutSeconds, TimeUnit.SECONDS)) {
            process.destroyForcibly()
            return ""
        }
        return parseWhisperOutput(output)
    }

    private fun parseWhisperOutput(raw: String): String {
        val lines = raw.lines().map { it.trim() }.filter { it.isNotBlank() }
        val text = StringBuilder()
        for (line in lines) {
            val t = line.replace(Regex("^\\s*\\[\\d+:\\d+\\.\\d+\\s*-->\\s*\\d+:\\d+\\.\\d+\\]\\s*"), "").trim()
            if (t.isNotBlank()) text.append(t).append(" ")
        }
        return text.toString().trim()
    }

    override fun release() {
        available = false
    }
}
