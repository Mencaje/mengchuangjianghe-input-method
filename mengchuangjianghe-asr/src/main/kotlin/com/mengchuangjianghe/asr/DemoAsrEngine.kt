package com.mengchuangjianghe.asr

/**
 * 演示/占位引擎：无外部依赖，直接返回示例文本。
 * 用于依赖拉取与集成测试通过；正式使用可替换为 HttpAsrEngine 或其它实现。
 */
class DemoAsrEngine : AsrEngine {

    override fun recognize(pcmData: ByteArray, sampleRate: Int): AsrResult {
        if (pcmData.isEmpty()) return AsrResult("", 0f, true)
        return AsrResult(
            text = "萌创匠盒语音识别演示",
            confidence = 0.95f,
            isFinal = true
        )
    }

    override fun isAvailable(): Boolean = true
}
