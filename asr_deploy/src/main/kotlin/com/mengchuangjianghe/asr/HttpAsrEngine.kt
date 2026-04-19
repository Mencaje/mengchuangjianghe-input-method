package com.mengchuangjianghe.asr

import java.io.OutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.nio.charset.StandardCharsets

/**
 * 基于 HTTP 的普通话语音识别（可对接百度/腾讯等 ASR 接口）。
 * 不引用任何 Android 依赖，纯 JVM 实现。
 */
class HttpAsrEngine(
    private val apiUrl: String,
    private val apiKey: String? = null,
    private val format: String = "pcm",
    private val connectTimeoutMs: Int = 10000,
    private val readTimeoutMs: Int = 30000
) : AsrEngine {

    private var available = apiUrl.isNotBlank()

    override fun isAvailable(): Boolean = available

    override fun recognize(pcmData: ByteArray, sampleRate: Int): AsrResult {
        if (!available || pcmData.isEmpty()) {
            return AsrResult(if (pcmData.isEmpty()) "" else "未配置或不可用", 0f, true)
        }
        return doPost(pcmData, sampleRate)
    }

    private fun doPost(pcmData: ByteArray, sampleRate: Int): AsrResult {
        var conn: HttpURLConnection? = null
        try {
            val url = URL(apiUrl)
            conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.connectTimeout = connectTimeoutMs
            conn.readTimeout = readTimeoutMs
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "audio/$format; rate=$sampleRate")
            apiKey?.let { conn.setRequestProperty("Authorization", "Bearer $it") }
            conn.outputStream.use { os: OutputStream ->
                os.write(pcmData)
                os.flush()
            }
            val code = conn.responseCode
            if (code != 200) {
                val err = conn.errorStream?.reader(StandardCharsets.UTF_8)?.readText() ?: "HTTP $code"
                return AsrResult("识别请求失败: $err", 0f, true)
            }
            val body = conn.inputStream.reader(StandardCharsets.UTF_8).readText()
            return parseResponse(body)
        } catch (e: Exception) {
            return AsrResult("识别异常: ${e.message}", 0f, true)
        } finally {
            conn?.disconnect()
        }
    }

    /**
     * 解析服务端 JSON。子类可重写以适配不同 ASR 接口。
     * 默认期望简单 JSON 如 {"text":"识别结果"} 或 {"result":["结果"]}
     */
    protected open fun parseResponse(body: String): AsrResult {
        val t = body.trim()
        if (t.isEmpty()) return AsrResult("", 0f, true)
        var text = ""
        if (t.contains("\"text\"")) {
            val start = t.indexOf("\"text\"") + 6
            var i = t.indexOf(':', start)
            if (i >= 0) {
                i = t.indexOf('"', i) + 1
                val end = t.indexOf('"', i)
                if (end > i) text = t.substring(i, end)
            }
        }
        if (text.isEmpty() && t.contains("\"result\"")) {
            val start = t.indexOf("\"result\"") + 8
            var i = t.indexOf('[', start)
            if (i >= 0) {
                i = t.indexOf('"', i) + 1
                val end = t.indexOf('"', i)
                if (end > i) text = t.substring(i, end)
            }
        }
        if (text.isEmpty()) text = t
        return AsrResult(text, 0.9f, true)
    }

    override fun release() {
        available = false
    }
}
