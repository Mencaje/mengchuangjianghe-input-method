package com.mengchuangbox.input

import android.content.Context
import net.sourceforge.pinyin4j.PinyinHelper
import net.sourceforge.pinyin4j.format.HanyuPinyinCaseType
import net.sourceforge.pinyin4j.format.HanyuPinyinOutputFormat
import net.sourceforge.pinyin4j.format.HanyuPinyinToneType
import net.sourceforge.pinyin4j.format.HanyuPinyinVCharType
import net.sourceforge.pinyin4j.format.exception.BadHanyuPinyinOutputFormatCombination
import java.io.BufferedReader
import java.io.InputStreamReader

/**
 * 拼音→汉字候选。字表由算法生成（CJK 区段 + Pinyin4j）；词表从 assets/pinyin_words.txt 加载，非硬编码。
 *
 * 词库共用：九宫格、26键、手写、笔画等所有输入法均使用本词库与联想数据（getAssociationPhrases/getAssociationCandidates）。
 * 主词库为 assets/pinyin_words.txt；另合并 car_brands、pinyin_words_poetry/food/countries/modern、pinyin_append_temp、
 * wordlist_idioms、wordlist_astronomy、wordlist_daily、pinyin_words_extended_batch_a（脚本去重生成）。
 * 同音字顺序：assets/char_frequency_weights.txt（脚本 build_char_frequency_from_wordlists.py：词库计数 + 通用字序加成）。
 * 可选 assets/char_frequency_general_rank.txt（每行一字，自上而下越常用）与脚本内置高频字序合并后参与加成。
 * 整句候选：可选 librime；就绪时 **Rime 候选优先**，并与本地合并词库 **拼接去重**（避免仅依赖一方导致未覆盖词条「全灰」），见 doc/RIME.md。
 * 增词可扩写上述任一 UTF-8 文本（每行：全小写拼音 词语）；大批量可用 scripts/generate_deduped_wordlist_batch.py。
 */
object PinyinDict {

    private val pinyinFormat = HanyuPinyinOutputFormat().apply {
        toneType = HanyuPinyinToneType.WITHOUT_TONE
        caseType = HanyuPinyinCaseType.LOWERCASE
        vCharType = HanyuPinyinVCharType.WITH_V
    }

    @Volatile
    private var pinyinToChars: Map<String, List<String>> = emptyMap()

    /** 合法音节集合，用于音节切分（由字表键集得出，非硬编码） */
    @Volatile
    private var validSyllables: Set<String> = emptySet()

    /** 拼音→词（多字），从 assets 词库文件加载 */
    @Volatile
    private var pinyinToWords: Map<String, List<String>> = emptyMap()

    /** 联想：上一字 → 词库中常接的下一字（如 你→[好,们]，用于词组联想/预测） */
    @Volatile
    private var charToNextChars: Map<String, List<String>> = emptyMap()

    /** 下一词预测：上一字 → 以该字开头的词（如 你→[你好,你们,你好呀]） */
    @Volatile
    private var charToPhrases: Map<String, List<String>> = emptyMap()

    /** 首字母联想：首字母串 → 词（如 nh→[你好]，djh→[大家好]），需在 validSyllables 就绪后构建 */
    @Volatile
    private var abbrToWords: Map<String, List<String>> = emptyMap()

    /** 从 abbr_words.txt 加载的首字母词库（两字母键 → 词列表），在 buildAbbreviationIndex 中合并 */
    @Volatile
    private var abbrWordsFromFile: Map<String, List<String>> = emptyMap()

    /** 首字母联想权重：键 → (词 → 权重)，权重越大候选越靠前；来自 abbr_weighted.txt */
    @Volatile
    private var abbrWordWeights: Map<String, Map<String, Int>> = emptyMap()

    /** 远程词库（静态托管 TXT 拉取后合并）：拼音 → 词列表。留口子：本地没有时可由应用拉取 URL 填入 */
    @Volatile
    private var remotePinyinToWords: Map<String, List<String>> = emptyMap()

    /** 单字补充：拼音 → 字（从词库文件中单字行合并进 pinyinToChars，补全 Pinyin4j 未覆盖的字） */
    @Volatile
    private var singleCharSupplement: Map<String, List<String>> = emptyMap()

    /** 汉字在合并词库中的累计权重（越高越靠前）；未收录字视为 0 */
    @Volatile
    private var charFrequencyWeights: Map<String, Int> = emptyMap()

    @Volatile
    private var buildStarted = false

    private fun charCorpusWeight(ch: String): Int = charFrequencyWeights[ch] ?: 0

    /** 词在词库中的粗权重（各汉字权重之和），用于整词排序 */
    private fun wordCorpusWeight(word: String): Int {
        var s = 0
        for (ch in word) {
            if (ch.code >= 0x3400) s += charCorpusWeight(ch.toString())
        }
        return s
    }

    private val wordFreqComparator: Comparator<String> =
        compareByDescending<String> { wordCorpusWeight(it) }.thenBy { it }

    /**
     * 合并候选列表：primary 全部优先排列（保持各自顺序），再追加 secondary 中尚未出现的项。
     */
    private fun mergeCandidateListsPreferPrimary(primary: List<String>, secondary: List<String>, limit: Int): List<String> {
        val seen = LinkedHashSet<String>()
        val out = mutableListOf<String>()
        for (x in primary) {
            if (out.size >= limit) break
            if (seen.add(x)) out.add(x)
        }
        for (x in secondary) {
            if (out.size >= limit) break
            if (seen.add(x)) out.add(x)
        }
        return out
    }

    @JvmStatic
    fun init(context: Context) {
        if (buildStarted) return
        buildStarted = true
        loadWordList(context)
        Thread {
            val map = mutableMapOf<String, MutableList<String>>()
            for (codePoint in 0x4E00..0x9FFF) {
                val c = codePoint.toChar()
                try {
                    val py = PinyinHelper.toHanyuPinyinStringArray(c, pinyinFormat) ?: continue
                    for (p in py) {
                        val key = p.trim().lowercase().replace("ü", "v")
                        if (key.isEmpty()) continue
                        map.getOrPut(key) { mutableListOf() }.add(c.toString())
                    }
                } catch (_: BadHanyuPinyinOutputFormatCombination) { }
            }
            for ((py, list) in singleCharSupplement) {
                map.getOrPut(py) { mutableListOf() }.addAll(list)
            }
            val charMap = map.mapValues { (_, list) ->
                list.distinct().sortedWith(
                    compareByDescending<String> { charCorpusWeight(it) }.thenBy { it }
                )
            }
            pinyinToChars = charMap
            validSyllables = charMap.keys.toSet()
            buildAbbreviationIndex()
        }.start()
    }

    /** 重复字母容错：将连续重复字母压成单字（如 nihaao→nihao），便于切分 */
    @JvmStatic
    fun deduplicateRepeatedChars(input: String): String {
        if (input.length < 2) return input
        return input.replace(Regex("(.)\\1+"), "$1")
    }

    /**
     * 音节切分：把连续拼音串按合法音节切成多段（如 nihao→[ni, hao]），用 validSyllables 做前向最长匹配。
     * 不依赖硬编码音节表，音节集来自 Pinyin4j 字表键集。
     */
    @JvmStatic
    fun segmentPinyin(input: String): List<String> {
        val s = input.lowercase().trim()
        if (s.isEmpty()) return emptyList()
        val syllables = validSyllables
        if (syllables.isEmpty()) return emptyList()
        val maxLen = syllables.maxOfOrNull { it.length } ?: 6
        val result = mutableListOf<String>()
        var pos = 0
        while (pos < s.length) {
            var found = false
            for (len in minOf(maxLen, s.length - pos) downTo 1) {
                val seg = s.substring(pos, pos + len)
                if (seg in syllables) {
                    result.add(seg)
                    pos += len
                    found = true
                    break
                }
            }
            if (!found) {
                result.add(s.substring(pos, pos + 1))
                pos += 1
            }
        }
        return result
    }

    /**
     * 按切分后的音节组词：每个音节取一字，组合成多字候选（如 [ni,hao]→你+好→你好）。
     * 优先返回词库中有的词，再按音节字组合；词库用于排序，不硬编码词表也能出 你好。
     */
    @JvmStatic
    fun getCandidatesFromSegments(segments: List<String>): List<String> {
        if (segments.isEmpty()) return emptyList()
        val map = pinyinToChars
        if (map.isEmpty()) return emptyList()
        val joined = segments.joinToString("")
        val fromWordList = (pinyinToWords[joined] ?: emptyList()) + (remotePinyinToWords[joined] ?: emptyList()).distinct()
        if (segments.size == 1) {
            val chars = map[segments[0]] ?: emptyList()
            val wordsSorted = fromWordList.distinct().sortedWith(wordFreqComparator)
            return (chars + wordsSorted).distinct().take(50)
        }
        val charLists = segments.map { map[it] ?: emptyList() }
        if (charLists.any { it.isEmpty() }) {
            // 末尾为不完整音节（如 jix→[ji,x]）：用拼音前缀匹配词库，如 jix 匹配 jixu、jixi 等，优先出「继续」等
            val byKey = mutableListOf<Pair<String, List<String>>>()
            for ((py, words) in pinyinToWords) {
                if (py.startsWith(joined)) byKey.add(py to words)
            }
            for ((py, words) in remotePinyinToWords) {
                if (py.startsWith(joined)) byKey.add(py to words)
            }
            val prefixWords = byKey.sortedBy { it.first.length }.flatMap { it.second }
            return (fromWordList + prefixWords).distinct().sortedWith(wordFreqComparator).take(50)
        }
        // 多音节且词库有精确匹配（如 jixu→继续）：只出词库词，不出单字乱拼（丌四、丌仙等）
        if (fromWordList.isNotEmpty()) return fromWordList.distinct().sortedWith(wordFreqComparator).take(50)
        val combined = mutableListOf<String>()
        var limit = 30
        for (indices in productIndices(charLists.size) { charLists[it].size }) {
            if (limit-- <= 0) break
            val word = indices.mapIndexed { i, idx -> charLists[i][idx] }.joinToString("")
            if (word !in combined) combined.add(word)
        }
        return combined.distinct().sortedWith(wordFreqComparator).take(50)
    }

    private fun productIndices(dim: Int, size: (Int) -> Int): Sequence<IntArray> = sequence {
        val idx = IntArray(dim)
        while (true) {
            yield(idx.clone())
            var d = dim - 1
            while (d >= 0) {
                idx[d]++
                if (idx[d] < size(d)) break
                idx[d] = 0
                d--
            }
            if (d < 0) break
        }
    }

    /** 从 assets 合并额外词库（如 car_brands.txt），格式同 pinyin_words：pinyin 词 */
    private fun mergeWordListFromAsset(context: Context, filename: String, map: MutableMap<String, MutableList<String>>) {
        try {
            context.assets.open(filename).use { stream ->
                BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
                    reader.forEachLine { line ->
                        val t = line.trim()
                        if (t.isEmpty() || t.startsWith("#")) return@forEachLine
                        val space = t.indexOf(' ')
                        if (space <= 0) return@forEachLine
                        val py = t.substring(0, space).lowercase().replace(" ", "")
                        val word = t.substring(space).trim()
                        if (py.isNotEmpty() && word.isNotEmpty()) {
                            map.getOrPut(py) { mutableListOf() }.add(word)
                        }
                    }
                }
            }
        } catch (_: Exception) { }
    }

    private fun loadCharFrequencyWeights(context: Context) {
        val m = mutableMapOf<String, Int>()
        try {
            context.assets.open("char_frequency_weights.txt").use { stream ->
                BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
                    reader.forEachLine { line ->
                        val t = line.trim()
                        if (t.isEmpty() || t.startsWith("#")) return@forEachLine
                        val sp = t.indexOf('\t')
                        if (sp <= 0) return@forEachLine
                        val ch = t.substring(0, sp).trim()
                        val w = t.substring(sp + 1).trim().toIntOrNull() ?: return@forEachLine
                        if (ch.length == 1) m[ch] = w
                    }
                }
            }
        } catch (_: Exception) { }
        charFrequencyWeights = m
    }

    private fun loadWordList(context: Context) {
        loadCharFrequencyWeights(context)
        val map = mutableMapOf<String, MutableList<String>>()
        val singleChar = mutableMapOf<String, MutableList<String>>()
        try {
            context.assets.open("pinyin_words.txt").use { stream ->
                BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
                    reader.forEachLine { line ->
                        val t = line.trim()
                        if (t.isEmpty() || t.startsWith("#")) return@forEachLine
                        val space = t.indexOf(' ')
                        if (space <= 0) return@forEachLine
                        val py = t.substring(0, space).lowercase().replace(" ", "")
                        val word = t.substring(space).trim()
                        if (py.isNotEmpty() && word.isNotEmpty()) {
                            map.getOrPut(py) { mutableListOf() }.add(word)
                            if (word.length == 1) singleChar.getOrPut(py) { mutableListOf() }.add(word)
                        }
                    }
                }
            }
            mergeWordListFromAsset(context, "car_brands.txt", map)
            mergeWordListFromAsset(context, "pinyin_words_poetry.txt", map)
            mergeWordListFromAsset(context, "pinyin_words_food.txt", map)
            mergeWordListFromAsset(context, "pinyin_words_countries.txt", map)
            mergeWordListFromAsset(context, "pinyin_words_modern.txt", map)
            mergeWordListFromAsset(context, "pinyin_append_temp.txt", map)
            mergeWordListFromAsset(context, "wordlist_idioms.txt", map)
            mergeWordListFromAsset(context, "wordlist_astronomy.txt", map)
            mergeWordListFromAsset(context, "wordlist_daily.txt", map)
            mergeWordListFromAsset(context, "pinyin_words_extended_batch_a.txt", map)
            pinyinToWords = map.mapValues { it.value.distinct() }
            singleCharSupplement = singleChar.mapValues { it.value.distinct() }
            buildAssociationMap()
        } catch (_: Exception) { }
        try {
            val abbrMap = mutableMapOf<String, MutableList<String>>()
            context.assets.open("abbr_words.txt").use { stream ->
                BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
                    reader.forEachLine { line ->
                        val t = line.trim()
                        if (t.isEmpty() || t.startsWith("#")) return@forEachLine
                        val parts = t.split("\\s+".toRegex())
                        if (parts.size < 2) return@forEachLine
                        val key = parts[0].lowercase()
                        if (key.length != 2) return@forEachLine
                        parts.drop(1).filter { it.isNotEmpty() }.forEach { w ->
                            abbrMap.getOrPut(key) { mutableListOf() }.add(w)
                        }
                    }
                }
            }
            abbrWordsFromFile = abbrMap.mapValues { it.value.distinct() }
            // 带权重的首字母词库 abbr_weighted.txt：每行「KEY 词 权重」，权重越大越靠前
            val weightMap = mutableMapOf<String, MutableMap<String, Int>>()
            try {
                context.assets.open("abbr_weighted.txt").use { stream ->
                    BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
                        reader.forEachLine { line ->
                            val t = line.trim()
                            if (t.isEmpty() || t.startsWith("#")) return@forEachLine
                            val parts = t.split("\\s+".toRegex())
                            if (parts.size < 3) return@forEachLine
                            val key = parts[0].lowercase()
                            if (key.length != 2) return@forEachLine
                            val word = parts[1]
                            val weight = parts[2].toIntOrNull() ?: return@forEachLine
                            if (word.isEmpty()) return@forEachLine
                            abbrMap.getOrPut(key) { mutableListOf() }.add(word)
                            weightMap.getOrPut(key) { mutableMapOf() }[word] = weight
                        }
                    }
                }
            } catch (_: Exception) { }
            abbrWordWeights = weightMap.mapValues { it.value.toMap() }
            abbrWordsFromFile = abbrMap.mapValues { it.value.distinct() }
        } catch (_: Exception) { }
    }

    /** 从词库构建「上一字→下一字」联想表 + 「上一字→下一词」预测表 */
    private fun buildAssociationMap() {
        val nextMap = mutableMapOf<String, MutableSet<String>>()
        val phraseMap = mutableMapOf<String, MutableSet<String>>()
        for (words in pinyinToWords.values) {
            for (word in words) {
                if (word.isEmpty()) continue
                phraseMap.getOrPut(word[0].toString()) { mutableSetOf() }.add(word)
                if (word.length < 2) continue
                for (i in 0..word.length - 2) {
                    val c = word[i].toString()
                    val next = word[i + 1].toString()
                    nextMap.getOrPut(c) { mutableSetOf() }.add(next)
                }
            }
        }
        charToNextChars = nextMap.mapValues { (_, set) -> set.toList() }
        charToPhrases = phraseMap.mapValues { (_, set) -> set.toList() }
    }

    /** 首字母联想索引：每个拼音串按音节取首字母（如 nihao→nh），并合并 abbr_words.txt 的两字母词库 */
    private fun buildAbbreviationIndex() {
        val abbr = mutableMapOf<String, MutableList<String>>()
        val syllables = validSyllables
        if (syllables.isNotEmpty()) {
            for ((py, words) in pinyinToWords) {
                val segs = segmentPinyin(py)
                if (segs.isEmpty()) continue
                val key = segs.map { it.first().toString() }.joinToString("")
                abbr.getOrPut(key) { mutableListOf() }.addAll(words)
            }
        }
        for ((key, words) in abbrWordsFromFile) {
            abbr.getOrPut(key) { mutableListOf() }.addAll(words)
        }
        abbrToWords = abbr.mapValues { it.value.distinct() }
    }

    /**
     * 联想候选：根据刚上屏的「上一字」给出词库中常接的下一字（如 你→好、们）。
     * 用于拼音缓冲为空时展示「下一个可能打的字」，实现词组联想/预测。
     */
    @JvmStatic
    fun getAssociationCandidates(prefixChar: String): List<String> {
        if (prefixChar.isEmpty()) return emptyList()
        val first = prefixChar.take(1)
        return charToNextChars[first] ?: emptyList()
    }

    /** 下一词预测：以该字开头的词（如 你→你好、你们、你好呀），联想栏可优先展示 */
    @JvmStatic
    fun getAssociationPhrases(prefixChar: String): List<String> {
        if (prefixChar.isEmpty()) return emptyList()
        val first = prefixChar.take(1)
        return charToPhrases[first] ?: emptyList()
    }

    /**
     * 根据「刚上屏的末字」把候选里 **下一字接得上词库 bigram** 的项前置（如 美 + li → 丽）。
     * 不依赖 librime；与 [getPinyinCandidates] 输出合并使用。
     */
    @JvmStatic
    fun boostCandidatesWithAssociation(prevCommittedTailChar: String?, candidates: List<String>): List<String> {
        if (prevCommittedTailChar.isNullOrEmpty() || candidates.isEmpty()) return candidates
        val prev = prevCommittedTailChar.take(1)
        val preferredNext = charToNextChars[prev]?.toSet() ?: return candidates
        val boosted = ArrayList<String>(candidates.size)
        val rest = ArrayList<String>()
        val seen = HashSet<String>()
        for (item in candidates) {
            if (item.isEmpty()) continue
            val head = item[0].toString()
            if (head in preferredNext && seen.add(item)) boosted.add(item)
        }
        for (item in candidates) {
            if (item !in seen) {
                rest.add(item)
                seen.add(item)
            }
        }
        boosted.addAll(rest)
        return boosted
    }

    /** 首字母联想：输入首字母串（如 nh、djh）得到词候选（你好、大家好等）；有权重时按权重降序排前 */
    @JvmStatic
    fun getAbbreviationCandidates(abbr: String): List<String> {
        val key = abbr.lowercase().trim()
        if (key.isEmpty()) return emptyList()
        val exact = abbrToWords[key] ?: emptyList()
        val prefix = abbrToWords.entries
            .filter { it.key.length > key.length && it.key.startsWith(key) }
            .flatMap { it.value }
        val combined = (exact + prefix).distinct()
        val weights = abbrWordWeights[key] ?: emptyMap()
        if (weights.isEmpty()) return combined
        return combined.sortedByDescending { weights[it] ?: 0 }
    }

    /** 本地词库 + 音节切分 + 首字母联想（不调用 librime）。 */
    private fun computeLegacyPinyinCandidates(raw: String): List<String> {
        val segments = segmentPinyin(raw)
        val segmentCands = if (segments.isNotEmpty()) getCandidatesFromSegments(segments) else emptyList()
        val abbrKeys = mutableListOf<String>()
        if (segments.size >= 2 && segments.last().length == 1) {
            abbrKeys.add(segments.map { it.first().toString() }.joinToString(""))
        }
        abbrKeys.add(raw)
        val abbrCands = mutableListOf<String>()
        for (key in abbrKeys) {
            for (w in getAbbreviationCandidates(key)) {
                if (w !in abbrCands) abbrCands.add(w)
            }
        }
        val singleCompleteSyllable =
            segments.size == 1 &&
                raw == segments[0] &&
                validSyllables.isNotEmpty() &&
                raw in validSyllables
        return if (singleCompleteSyllable) {
            mergeCandidateListsPreferPrimary(segmentCands, abbrCands, 50)
        } else {
            mergeCandidateListsPreferPrimary(abbrCands, segmentCands, 50)
        }
    }

    /**
     * 缓冲是否为 **单个完整音节**（如 li、mei），且与整串一致。
     * 用于：先上屏一字再输入下一音节时，只有此时才适合用本地 bigram 调整「力/丽」等同音次序（与整句连打 mei li 不同）。
     */
    @JvmStatic
    fun isBufferSingleCompleteSyllable(pinyinAscii: String): Boolean {
        val r = pinyinAscii.lowercase().trim().filter { it in 'a'..'z' }
        if (r.isEmpty() || validSyllables.isEmpty()) return false
        val segs = segmentPinyin(r)
        return segs.size == 1 && segs[0] == r && r in validSyllables
    }

    /**
     * 拼音候选栏：[words] 为合并列表；[rimePickSlots] 为可与 librime 当前页 [index] 对齐的前缀长度（用于上屏选词）。
     *
     * [prevCommittedTailChar]：刚上屏的末字；在 **单音节缓冲** 且 Rime 已就绪时，会用本地 bigram 把「丽」等邻接字前提，并令 [rimePickSlots]=0（因顺序已与 Rime 菜单不一致，改走按候选文本上屏）。
     */
    data class PinyinCandidateBar(val words: List<String>, val rimePickSlots: Int)

    private fun matchingPrefixLength(merged: List<String>, primary: List<String>): Int {
        var n = 0
        for (i in primary.indices) {
            if (i < merged.size && merged[i] == primary[i]) n++
            else break
        }
        return n
    }

    /**
     * 拼音候选统一入口：本地词库路径 +（若 librime 就绪）Rime 引擎与内置方案词库。
     * Rime 优先列出，其后拼接本地独有词条，减少「长句未覆盖时全无候选」。
     */
    @JvmStatic
    fun getPinyinCandidateBar(
        pinyin: String,
        prevCommittedTailChar: String? = null,
    ): PinyinCandidateBar {
        val raw = pinyin.lowercase().trim().filter { it in 'a'..'z' }
        if (raw.isEmpty()) return PinyinCandidateBar(emptyList(), 0)
        var legacy = computeLegacyPinyinCandidates(raw)
        if (!RimeEngine.isReady() && prevCommittedTailChar != null) {
            legacy = boostCandidatesWithAssociation(prevCommittedTailChar, legacy)
        }

        if (RimeEngine.isReady()) {
            RimeEngine.ensurePinyinSynced(raw)
            val rime = RimeEngine.currentRimeMenu()
            if (rime.isNotEmpty()) {
                val merged = mergeCandidateListsPreferPrimary(rime, legacy, 50)
                val slots = matchingPrefixLength(merged, rime)
                if (prevCommittedTailChar != null && isBufferSingleCompleteSyllable(raw)) {
                    val boosted = boostCandidatesWithAssociation(prevCommittedTailChar, merged)
                    return PinyinCandidateBar(boosted, 0)
                }
                return PinyinCandidateBar(merged, slots)
            }
            if (prevCommittedTailChar != null && isBufferSingleCompleteSyllable(raw)) {
                legacy = boostCandidatesWithAssociation(prevCommittedTailChar, legacy)
            }
            return PinyinCandidateBar(legacy, 0)
        }
        return PinyinCandidateBar(legacy, 0)
    }

    @JvmStatic
    fun getPinyinCandidates(pinyin: String, prevCommittedTailChar: String? = null): List<String> =
        getPinyinCandidateBar(pinyin, prevCommittedTailChar).words

    /** 设置远程词库（应用从静态托管 URL 拉取 TXT 解析后调用，与本地合并展示） */
    @JvmStatic
    fun setRemoteWordList(map: Map<String, List<String>>) {
        remotePinyinToWords = map
    }

    /** 词候选：整串拼音对应多字词（如 nihao→你好），本地 + 远程合并 */
    @JvmStatic
    fun getWordCandidates(pinyin: String): List<String> {
        val key = pinyin.lowercase().trim()
        if (key.isEmpty()) return emptyList()
        val local = pinyinToWords[key] ?: emptyList()
        val remote = remotePinyinToWords[key] ?: emptyList()
        return (local + remote).distinct()
    }

    @JvmStatic
    fun getCandidates(pinyin: String): List<String> {
        val map = pinyinToChars
        if (map.isEmpty()) return emptyList()
        val key = pinyin.lowercase().trim()
        if (key.isEmpty()) return emptyList()
        val exact = map[key]
        if (!exact.isNullOrEmpty()) return exact
        if (key.length <= 2) return getCandidatesByPrefix(key)
        return emptyList()
    }

    /** 前缀候选数量上限，避免单字母时返回过多导致 UI 卡死、影响连续输入 */
    private const val MAX_PREFIX_CANDIDATES = 80

    @JvmStatic
    fun getCandidatesByPrefix(prefix: String): List<String> {
        val map = pinyinToChars
        if (map.isEmpty()) return emptyList()
        val key = prefix.lowercase().trim()
        if (key.isEmpty()) return emptyList()
        return map.filterKeys { it.startsWith(key) }.values.flatten().distinct()
            .sortedWith(
                compareByDescending<String> { charCorpusWeight(it) }.thenBy { it }
            )
            .take(MAX_PREFIX_CANDIDATES)
    }

    /** 单字对应的拼音列表（去声调、去重），供 T9 九宫格等使用；多音字返回多个。 */
    @JvmStatic
    fun getPinyinForChar(c: Char): List<String> {
        if (c.code < 128) return emptyList()
        return try {
            val py = PinyinHelper.toHanyuPinyinStringArray(c, pinyinFormat) ?: return emptyList()
            py.map { it.trim().lowercase().replace("ü", "v") }.filter { it.isNotEmpty() }.distinct()
        } catch (_: BadHanyuPinyinOutputFormatCombination) {
            emptyList()
        }
    }

    /** 词的拼音串（每字取首音，供九宫格候选栏上方显示「当前按键对应的拼音」）。 */
    @JvmStatic
    fun getPinyinForWord(word: String): String = word.map { c ->
        if (c.code < 128) c.toString() else (getPinyinForChar(c).firstOrNull() ?: "")
    }.joinToString("")

    /** 词库中所有词（用于 T9 建索引），与 pinyin_words.txt 一致。 */
    @JvmStatic
    fun getAllWords(): List<String> = pinyinToWords.values.flatten().distinct()
}
