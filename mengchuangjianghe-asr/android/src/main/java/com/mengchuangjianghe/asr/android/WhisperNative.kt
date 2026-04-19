package com.mengchuangjianghe.asr.android

/**
 * 本地 Whisper 推理 JNI 桥接。
 * 加载 libmengchuangjianghe_asr_native.so，由 NDK 在构建时生成并打入 AAR/APK。
 */
object WhisperNative {

    private const val LIB_NAME = "mengchuangjianghe_asr_native"

    /** .so 是否已成功加载（依赖 android 模块并打包进 APK 时为 true，不请求系统语音服务） */
    @JvmStatic
    val isLibraryLoaded: Boolean by lazy {
        try {
            System.loadLibrary(LIB_NAME)
            true
        } catch (e: UnsatisfiedLinkError) {
            false
        }
    }

    /**
     * 从本地文件路径加载 Whisper 模型（如 ggml-base.en.bin）。
     * 接入真实 whisper.cpp 并传入有效路径时返回 true。
     */
    @JvmStatic
    external fun nativeLoadModel(modelPath: String?): Boolean

    /**
     * 将 PCM 送入本地引擎识别，返回文本。
     * @param pcmData 16bit 单声道小端 PCM
     * @param sampleRate 采样率，如 16000
     * @return 识别结果，未加载模型或占位实现时返回空字符串
     */
    @JvmStatic
    external fun nativeRecognize(pcmData: ByteArray?, sampleRate: Int): String?

    /**
     * 是否已加载本地模型（可用来决定是否走本地识别）
     */
    @JvmStatic
    external fun nativeIsModelLoaded(): Boolean
}
