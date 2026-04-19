package com.mengchuangjianghe.asr

/**
 * 语音识别结果。
 * @param text 识别出的文本（普通话转文字）
 * @param confidence 置信度 0~1，可选
 * @param isFinal 是否最终结果（流式时可为 false）
 */
data class AsrResult(
    val text: String,
    val confidence: Float = 1f,
    val isFinal: Boolean = true
) {
    fun isSuccess(): Boolean = text.isNotBlank()
}
