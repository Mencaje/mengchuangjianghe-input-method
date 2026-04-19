package com.mengchuangbox.input

import android.content.Context
import android.content.res.AssetManager
import java.io.File
import java.io.FileOutputStream

/**
 * Rime（librime）引擎门面：部署 assets/rime_shared → 用户目录，加载 librime_jni，供整句拼音候选。
 *
 * 默认 **STUB JNI**（未放置 librime.so）时 [ready] 为 false，26 键仍走本地 [PinyinDict]。
 * 放置预编译 librime + Rime 共享数据后 [ready] 为 true，[PinyinDict.getPinyinCandidates] **整段拼音优先只走 Rime**。
 */
object RimeEngine {

    data class PickResult(val commitText: String, val remainingPinyin: String)

    @Volatile
    private var libraryLoaded = false

    @Volatile
    private var ready = false

    /** 已与 [nativeUpdateAndGetCandidates] 同步的纯 a–z 串；分页仅刷新菜单时保持不变。 */
    @Volatile
    private var syncedPinyinKey: String? = null

    private val lock = Any()

    /** librime 已成功初始化且可作为主解码器（与 STUB 区分）。 */
    fun isReady(): Boolean = ready

    fun init(context: Context) {
        synchronized(lock) {
            if (ready) return
            try {
                if (!libraryLoaded) {
                    System.loadLibrary("rime_jni")
                    libraryLoaded = true
                }
            } catch (_: UnsatisfiedLinkError) {
                return
            }
            val sharedDir = deploySharedData(context)
            val userDir = File(context.filesDir, "rime/user").apply { mkdirs() }.absolutePath
            ready = try {
                if (RimeJni.nativeInit(sharedDir, userDir)) {
                    applyDefaultSchemaOptions()
                    true
                } else {
                    false
                }
            } catch (_: Throwable) {
                false
            }
        }
    }

    private fun applyDefaultSchemaOptions() {
        try {
            RimeJni.nativeSetOption("simplification", true)
        } catch (_: Throwable) {
        }
    }

    fun shutdown() {
        synchronized(lock) {
            syncedPinyinKey = null
            if (!libraryLoaded) return
            try {
                RimeJni.nativeShutdown()
            } catch (_: Throwable) {
            }
            ready = false
            libraryLoaded = false
        }
    }

    private fun normalizePinyinKey(raw: String): String =
        raw.lowercase().filter { it in 'a'..'z' }

    /**
     * 保证会话中的输入与 [raw]（仅 a–z）一致；空串时清空 librime 组字。
     */
    fun ensurePinyinSynced(raw: String) {
        if (!ready) return
        val k = normalizePinyinKey(raw)
        if (k.isEmpty()) {
            syncedPinyinKey = null
            try {
                RimeJni.nativeClearComposition()
            } catch (_: Throwable) {
            }
            return
        }
        if (k == syncedPinyinKey) return
        try {
            RimeJni.nativeUpdateAndGetCandidates(k)
            syncedPinyinKey = k
        } catch (_: Throwable) {
            syncedPinyinKey = null
        }
    }

    /** 当前页的 Rime 候选（须先 [ensurePinyinSynced]）。 */
    fun currentRimeMenu(): List<String> {
        if (!ready || syncedPinyinKey == null) return emptyList()
        return try {
            RimeJni.nativeGetCurrentCandidates().filter { it.isNotBlank() }
        } catch (_: Throwable) {
            emptyList()
        }
    }

    fun getPreedit(): String {
        if (!ready) return ""
        return try {
            RimeJni.nativeGetPreedit().trim()
        } catch (_: Throwable) {
            ""
        }
    }

    fun getRawInput(): String {
        if (!ready) return ""
        return try {
            normalizePinyinKey(RimeJni.nativeGetInput())
        } catch (_: Throwable) {
            ""
        }
    }

    fun flipCandidatePage(backward: Boolean): List<String> {
        if (!ready || syncedPinyinKey == null) return emptyList()
        return try {
            RimeJni.nativeFlipCandidatePage(backward).filter { it.isNotBlank() }
        } catch (_: Throwable) {
            emptyList()
        }
    }

    /**
     * 选取当前页第 [index] 项；返回上屏正文与剩余拼音（须据此更新缓冲区）。
     */
    fun pickCandidateOnCurrentPage(index: Int): PickResult? {
        if (!ready) return null
        return try {
            val commit = RimeJni.nativePickCandidateOnCurrentPage(index) ?: return null
            val rest = normalizePinyinKey(RimeJni.nativeGetInput())
            syncedPinyinKey = rest.ifEmpty { null }
            PickResult(commit, rest)
        } catch (_: Throwable) {
            null
        }
    }

    fun setOption(option: String, value: Boolean) {
        if (!ready) return
        try {
            RimeJni.nativeSetOption(option, value)
        } catch (_: Throwable) {
        }
    }

    /**
     * 将当前完整拼音串（仅 a–z）交给 Rime，返回当前页候选（与旧逻辑兼容）。
     */
    fun candidatesForPinyin(fullPinyin: String): List<String> {
        if (!ready) return emptyList()
        val raw = normalizePinyinKey(fullPinyin)
        if (raw.isEmpty()) return emptyList()
        ensurePinyinSynced(fullPinyin)
        return currentRimeMenu()
    }

    private fun deploySharedData(context: Context): String {
        val dest = File(context.filesDir, "rime/share")
        dest.mkdirs()
        try {
            copyAssetFolder(context.assets, "rime_shared", dest)
        } catch (_: Throwable) {
        }
        return dest.absolutePath
    }

    private fun copyAssetFolder(assets: AssetManager, assetPath: String, destDir: File) {
        val list = assets.list(assetPath) ?: return
        if (list.isEmpty()) return
        for (name in list) {
            val sub = "$assetPath/$name"
            val children = assets.list(sub)
            if (children.isNullOrEmpty()) {
                copySingleAsset(assets, sub, File(destDir, name))
            } else {
                val next = File(destDir, name)
                next.mkdirs()
                copyAssetFolder(assets, sub, next)
            }
        }
    }

    private fun copySingleAsset(assets: AssetManager, assetPath: String, destFile: File) {
        destFile.parentFile?.mkdirs()
        assets.open(assetPath).use { input ->
            FileOutputStream(destFile).use { output ->
                input.copyTo(output)
            }
        }
    }
}
