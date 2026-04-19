package com.mengchuangjianghe.asr.android

import com.mengchuangjianghe.asr.AsrEngine
import com.mengchuangjianghe.asr.AsrResult
import com.mengchuangjianghe.asr.TextRefiner

/**
 * 基于打包进 APK 的 .so 的本地语音识别引擎。
 * 不依赖系统 SpeechRecognizer：只要 .so 已打包并加载成功就走本地采集+识别，不请求系统语音服务。
 */
class WhisperNativeEngine : AsrEngine {

    /** 只要本地 .so 已加载就视为可用，不再依赖系统 SpeechRecognizer */
    override fun isAvailable(): Boolean = WhisperNative.isLibraryLoaded

    override fun recognize(pcmData: ByteArray, sampleRate: Int): AsrResult {
        if (pcmData.isEmpty()) return AsrResult("", 0f, true)
        val raw = try {
            WhisperNative.nativeRecognize(pcmData, sampleRate)?.trim().orEmpty()
        } catch (_: Throwable) {
            ""
        }
        val text = if (raw.isNotEmpty()) TextRefiner.refine(raw) else ""
        return AsrResult(text, if (text.isNotEmpty()) 0.9f else 0f, true)
    }
}
