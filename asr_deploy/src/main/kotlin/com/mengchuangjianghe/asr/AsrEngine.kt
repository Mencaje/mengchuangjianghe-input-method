package com.mengchuangjianghe.asr

/**
 * 语音转文字引擎接口（普通话识别）。
 * 不依赖 Android，纯 JVM，便于任意项目通过一行依赖拉取使用。
 */
interface AsrEngine {

    /**
     * 识别 PCM 音频为文字。
     * @param pcmData 16bit 单声道 PCM 原始数据（小端）
     * @param sampleRate 采样率，如 16000
     * @return 识别结果，失败时 text 为空或包含错误信息
     */
    fun recognize(pcmData: ByteArray, sampleRate: Int): AsrResult

    /**
     * 是否可用（如网络引擎未配置 key 时可为 false）
     */
    fun isAvailable(): Boolean = true

    /**
     * 释放资源（如网络连接、本地模型等）
     */
    fun release() {}
}
