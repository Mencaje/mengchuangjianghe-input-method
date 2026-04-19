package com.mengchuangbox.input

/**
 * librime JNI 入口（实现见 app/src/main/cpp/rime_jni.cpp）。
 * 默认编译为 STUB：nativeInit 为 false，候选为空；接入真实 librime 后见 doc/RIME.md。
 */
@Suppress("unused")
internal object RimeJni {
    @JvmStatic
    external fun nativeInit(sharedDir: String, userDir: String): Boolean

    /** 清空组字、模拟整段拼音字母序列，返回当前页候选（简体等由方案决定）。 */
    @JvmStatic
    external fun nativeUpdateAndGetCandidates(keys: String): Array<String>

    /** 不重置输入，仅读取当前组字下的候选页（须先 [nativeUpdateAndGetCandidates] 同步同一拼音串）。 */
    @JvmStatic
    external fun nativeGetCurrentCandidates(): Array<String>

    /** false=下一页，true=上一页（与 librime change_page 一致）。 */
    @JvmStatic
    external fun nativeFlipCandidatePage(backward: Boolean): Array<String>

    @JvmStatic
    external fun nativePickCandidateOnCurrentPage(index: Int): String?

    /** 组字区展示用（如带音节边界的 preedit）。 */
    @JvmStatic
    external fun nativeGetPreedit(): String

    /** 原始 ASCII 输入缓冲（选词后剩余拼音等），与界面拼音串对齐用。 */
    @JvmStatic
    external fun nativeGetInput(): String

    @JvmStatic
    external fun nativeSetOption(option: String, value: Boolean)

    @JvmStatic
    external fun nativeClearComposition()

    @JvmStatic
    external fun nativeShutdown()
}
