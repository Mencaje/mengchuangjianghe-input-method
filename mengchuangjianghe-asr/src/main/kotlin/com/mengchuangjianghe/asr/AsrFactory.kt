package com.mengchuangjianghe.asr

/**
 * 创建 ASR 引擎的入口。
 * 本库为纯本地算法，基于 OpenAI Whisper 开源项目（MIT）优化集成，不调用任何第三方接口。
 */
object AsrFactory {

    /**
     * 演示引擎（仅用于依赖与集成测试）
     */
    @JvmStatic
    fun createDemo(): AsrEngine = DemoAsrEngine()

    /**
     * 纯本地识别引擎：基于 OpenAI Whisper（MIT），需本地已安装 whisper.cpp 或兼容可执行程序及模型。
     * @param modelPath 模型文件路径（如 ggml-base.bin）
     * @param executablePath 可执行程序路径或命令（如 main 或 whisper.cpp 编译出的 main）
     */
    @JvmStatic
    fun createWhisper(
        modelPath: String,
        executablePath: String = "main",
        processTimeoutSeconds: Long = 60L
    ): AsrEngine = WhisperAsrEngine(modelPath, executablePath, processTimeoutSeconds)

    /**
     * 可选：对接自建或第三方 HTTP 接口（非本库算法，仅方便扩展）
     */
    @JvmStatic
    fun createHttp(
        apiUrl: String,
        apiKey: String? = null,
        format: String = "pcm",
        connectTimeoutMs: Int = 10000,
        readTimeoutMs: Int = 30000
    ): AsrEngine = HttpAsrEngine(apiUrl, apiKey, format, connectTimeoutMs, readTimeoutMs)

    /**
     * 默认引擎：本地可用时优先 Whisper；否则为演示引擎。
     * 生产环境请使用 createWhisper(modelPath, executablePath) 并确保本地已部署 Whisper。
     */
    @JvmStatic
    fun createDefault(): AsrEngine = createDemo()
}
