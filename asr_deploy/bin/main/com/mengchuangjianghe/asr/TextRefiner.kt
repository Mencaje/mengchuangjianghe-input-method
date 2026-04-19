package com.mengchuangjianghe.asr

/**
 * 根据识别文本做修辞与规整，使结果更精准、可读。
 */
object TextRefiner {

    @JvmStatic
    fun refine(recognized: String): String {
        if (recognized.isBlank()) return ""
        var s = recognized.replace(Regex("\\s+"), " ").trim()
        if (s.isEmpty()) return ""
        val last = s.last()
        val needPeriod = last in '\u4e00'..'\u9fff' || last in '0'..'9' || last in 'a'..'z' || last in 'A'..'Z'
        return if (needPeriod) "$s。" else s
    }
}
