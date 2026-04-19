package com.mengchuangjianghe.asr

import org.junit.Assert.*
import org.junit.Test

class AsrEngineTest {

    @Test
    fun demoEngineReturnsText() {
        val engine = AsrFactory.createDemo()
        assertTrue(engine.isAvailable())
        val result = engine.recognize(ByteArray(1600), 16000)
        assertTrue(result.isSuccess())
        assertTrue(result.text.isNotBlank())
        assertTrue(result.confidence > 0)
    }

    @Test
    fun demoEngineEmptyInputReturnsEmpty() {
        val engine = AsrFactory.createDemo()
        val result = engine.recognize(ByteArray(0), 16000)
        assertFalse(result.isSuccess())
        assertTrue(result.text.isEmpty())
    }

    @Test
    fun createDefaultWorks() {
        val engine = AsrFactory.createDefault()
        assertNotNull(engine)
        assertTrue(engine.isAvailable())
    }
}
