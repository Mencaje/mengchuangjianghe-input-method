package com.mengchuangjianghe.asr.android

import android.content.Context
import com.mengchuangjianghe.asr.AsrEngine
import java.io.File
import java.io.FileOutputStream

/**
 * Android 端 ASR 入口：提供打包在 APK 内的本地 .so 引擎。
 * 添加本库依赖并构建后，算法自动以 native 库形式打入 APK，不依赖系统语音服务。
 */
object AsrAndroid {

    private const val MODEL_SUBDIR = "whisper"
    /** 默认 assets 中的模型文件名（tiny 体积小适合首包，支持中英文；可用脚本 download_whisper_model.ps1 下载） */
    const val DEFAULT_MODEL_ASSET = "ggml-tiny.bin"

    /**
     * 创建本地 .so 引擎。
     */
    @JvmStatic
    fun createNativeEngine(): AsrEngine = WhisperNativeEngine()

    /**
     * 从 assets 复制模型到应用目录并加载，供语音转文字 1.0 使用。
     * 需在 app 的 assets 下放置 ggml 模型（如 ggml-base.en.bin），或指定 [assetFileName]。
     * @return true 表示加载成功（native 已接入 whisper 且模型有效），false 表示未接入或失败
     */
    @JvmStatic
    @JvmOverloads
    fun loadModelFromAssets(context: Context, assetFileName: String = DEFAULT_MODEL_ASSET): Boolean {
        if (!WhisperNative.isLibraryLoaded) return false
        val dir = File(context.filesDir, MODEL_SUBDIR).apply { mkdirs() }
        val outFile = File(dir, assetFileName)
        if (!outFile.exists()) {
            try {
                context.assets.open(assetFileName).use { input ->
                    FileOutputStream(outFile).use { output ->
                        input.copyTo(output)
                    }
                }
            } catch (e: Exception) {
                return false
            }
        }
        return WhisperNative.nativeLoadModel(outFile.absolutePath)
    }

    /** 是否已加载模型（仅当 native 接入 whisper 且调过 [loadModelFromAssets] 成功时为 true） */
    @JvmStatic
    fun isModelLoaded(): Boolean = WhisperNative.isLibraryLoaded && WhisperNative.nativeIsModelLoaded()
}
