package com.mengchuangjianghe.asr

/**
 * 根据识别文本做修辞与规整，使结果更精准、可读。
 * 在识别结果上做：去多余空格、句末标点、简单规整。
 */
object TextRefiner {

    /**
     * 对识别得到的文本做修辞与规整。
     * @param recognized 原始识别文本（如 ASR 返回的 text）
     * @return 规整后的文本，适合直接上屏
     */
    @JvmStatic
    fun refine(recognized: String): String {
        if (recognized.isBlank()) return ""
        var s = recognized
            .replace(Regex("\\s+"), " ")
            .trim()
        if (s.isEmpty()) return ""
        // 句末无标点时补句号（中英文混排时常见）
        val last = s.last()
        val punct = "，。！？；：\"\"''」）】"
        if (last in '0'..'9' || last in 'a'..'z' || last in 'A'..'Z' ||
            last in '\u4e00'..'\u9fff' || last in punct
        ) {
            if (last in '\u4e00'..'\u9fff' || last in '0'..'9' || last in 'a'..'z' || last in 'A'..'Z')
                s = "$s。"
        }
        return s
    }
}
