package com.mengchuangjianghe.asr

/**
 * 创建 ASR 引擎的入口。
 * 本库为纯本地算法，基于 OpenAI Whisper 开源项目（MIT）优化集成，不调用任何第三方接口。
 */
object AsrFactory {

    @JvmStatic
    fun createDemo(): AsrEngine = DemoAsrEngine()

    @JvmStatic
    fun createWhisper(
        modelPath: String,
        executablePath: String = "main",
        processTimeoutSeconds: Long = 60L
    ): AsrEngine = WhisperAsrEngine(modelPath, executablePath, processTimeoutSeconds)

    @JvmStatic
    fun createHttp(
        apiUrl: String,
        apiKey: String? = null,
        format: String = "pcm",
        connectTimeoutMs: Int = 10000,
        readTimeoutMs: Int = 30000
    ): AsrEngine = HttpAsrEngine(apiUrl, apiKey, format, connectTimeoutMs, readTimeoutMs)

    @JvmStatic
    fun createDefault(): AsrEngine = createDemo()
}
