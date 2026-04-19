# mengchuangjianghe-asr

萌创匠盒语音转文字模块（ASR），**纯本地算法**：基于 [OpenAI Whisper](https://github.com/openai/whisper) 开源库进行优化与集成，**不调用任何第三方接口**，全部识别在本地完成。

**不依赖 Android**，纯 JVM 库，一行依赖即可接入。开源算法优于闭源接口，可审计、可离线、可二次优化。

## 版权与开源协议

- 本库识别核心基于 **OpenAI Whisper**（[MIT License](https://github.com/openai/whisper/blob/main/LICENSE)）。
- 使用本库时请遵守 Whisper 的 MIT 协议，并保留版权与许可声明。详见项目 **[NOTICE](NOTICE)** 文件。

## 添加依赖（一行）

### Gradle (Kotlin DSL)

```kotlin
repositories {
    maven { url = uri("https://jitpack.io") }
}
dependencies {
    implementation("com.github.Mencaje:mengchuangjianghe-asr:1.3.0")
}
```

### Gradle (Groovy)

```groovy
repositories {
    maven { url 'https://jitpack.io' }
}
dependencies {
    implementation 'com.github.Mencaje:mengchuangjianghe-asr:1.3.0'
}
```

## 纯本地识别（推荐）

需在本地部署 **Whisper**（如 [whisper.cpp](https://github.com/ggerganov/whisper.cpp)）及模型文件，本库通过调用本地可执行程序完成识别，无任何网络请求。

```kotlin
import com.mengchuangjianghe.asr.AsrFactory
import com.mengchuangjianghe.asr.AsrResult
import com.mengchuangjianghe.asr.TextRefiner

// 本地 Whisper 引擎：模型路径 + 可执行程序路径（如 whisper.cpp 编译出的 main）
val engine = AsrFactory.createWhisper(
    modelPath = "/path/to/ggml-base.bin",
    executablePath = "/path/to/main"  // 或系统 PATH 下的 "main"
)

val pcmData: ByteArray = ... // 16kHz 16bit 单声道 PCM
val result: AsrResult = engine.recognize(pcmData, 16000)
if (result.isSuccess()) {
    val text = TextRefiner.refine(result.text)
    println(text)
}
```

### 部署 Whisper 本地环境

1. 克隆并编译 [whisper.cpp](https://github.com/ggerganov/whisper.cpp)，得到可执行文件 `main`。
2. 下载 ggml 模型（如 `ggml-base.bin`）至本地目录。
3. 将 `modelPath` 与 `executablePath` 传入 `createWhisper` 即可。

## 其他用法

- **仅集成测试**：`AsrFactory.createDemo()`（返回固定示例文本，不调用 Whisper）
- **自建/第三方 HTTP 接口**（非本库算法）：`AsrFactory.createHttp(apiUrl = "...", apiKey = "...")`

## 接口说明

- **AsrEngine**：`recognize(pcmData, sampleRate)`、`isAvailable()`、`release()`
- **AsrResult**：`text`、`confidence`、`isFinal`
- **TextRefiner**：`refine(recognized)`，修辞规整
- **AsrFactory**：`createWhisper(modelPath, executablePath)`（纯本地）、`createDemo()`、`createHttp(...)`、`createDefault()`

## 本地构建

```bash
./gradlew build
```

## 版本与发布

版本在 `build.gradle.kts` 中指定；打 tag（如 `1.3.0`）并推送到 GitHub 后，JitPack 自动构建。

## License

Apache-2.0。本库使用的 Whisper 相关组件见 [NOTICE](NOTICE)。
