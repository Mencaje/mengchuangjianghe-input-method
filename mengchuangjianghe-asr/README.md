# mengchuangjianghe-asr

萌创匠盒语音转文字模块（ASR），**纯本地算法**：基于 [OpenAI Whisper](https://github.com/openai/whisper) 与 [whisper.cpp](https://github.com/ggml-org/whisper.cpp) 集成，**不调用任何第三方接口**，全部识别在设备本地完成。

- **Android**：一行依赖接入，构建时自动将识别引擎编译为 native 库（.so）打入 APK，**不依赖系统语音服务**，避免「未选择语音识别服务」「绑定失败」等问题。
- **JVM**：纯 Kotlin 库，可单独用于服务端或桌面。

仓库地址：[https://github.com/Mencaje/mengchuangjianghe-asr](https://github.com/Mencaje/mengchuangjianghe-asr)

---

## 版权与开源协议

- 本库识别核心基于 **OpenAI Whisper**（[MIT License](https://github.com/openai/whisper/blob/main/LICENSE)）及 **whisper.cpp**（MIT）。
- 使用本库时请遵守上述协议并保留版权与许可声明。详见 **[NOTICE](NOTICE)**。

---

## 添加依赖（一行）

### Android 应用（推荐：.so 打包进 APK，不连系统）

在应用 `build.gradle.kts` 中：

```kotlin
repositories {
    maven { url = uri("https://jitpack.io") }
}
dependencies {
    implementation("com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0")
}
```

在代码中使用本地引擎（采集 PCM，松手后识别上屏）：

```kotlin
import com.mengchuangjianghe.asr.android.AsrAndroid

val engine = AsrAndroid.createNativeEngine()
if (engine.isAvailable()) {
    // 长按录音 -> 松手后 engine.recognize(pcm, 16000) 得到文本
    val result = engine.recognize(pcmData, 16000)
    if (result.text.isNotBlank()) commitText(TextRefiner.refine(result.text))
} else {
    // 可选：回退到系统 SpeechRecognizer
}
```

### 纯 JVM / 服务端（无 Android）

```kotlin
dependencies {
    implementation("com.github.Mencaje:mengchuangjianghe-asr:1.3.0")
}
```

### Gradle (Groovy)

```groovy
repositories { maven { url 'https://jitpack.io' } }
dependencies {
    implementation 'com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0'  // Android
    // implementation 'com.github.Mencaje:mengchuangjianghe-asr:1.3.0'      // JVM only
}
```

---

## 语音转文字 1.0 跑通（Android 说话出字）

要让「长按说话 → 松手出字」真正可用，只需两步。

### 1. 启用 Whisper 构建（默认已开）

- 本库 `gradle.properties` 中已设 `useWhisper=true`，构建 **android** 模块时会通过 CMake FetchContent 拉取并编译 [whisper.cpp](https://github.com/ggml-org/whisper.cpp)，无需自行编译 libwhisper.a。
- **首次构建** 会下载 whisper 源码，耗时约数分钟；之后增量构建正常。
- 若不需要真实识别（仅占位 so）：在 `gradle.properties` 中设 `useWhisper=false`。

### 2. 模型文件放入 App 的 assets

- 将 ggml 模型放到**使用本库的 Android 应用**的 `app/src/main/assets/` 下，默认文件名为 **`ggml-tiny.bin`**（支持中英文，体积较小）。
- **下载方式**：
  - 在应用工程根目录执行（PowerShell）：`.\scripts\download_whisper_model.ps1 -Model tiny`
  - 或从 [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin) 下载后放入 `app/src/main/assets/`。
- 首次长按语音时，库会从 assets 复制到应用私有目录并加载；之后即可识别出字。

### 3. 应用侧调用（示例）

- 长按触发录音，松手后调用 `AsrAndroid.loadModelFromAssets(context)`（若尚未加载），再 `engine.recognize(pcm, 16000)`。
- 默认从 assets 读取 `ggml-tiny.bin`；若使用其他文件名，可调用 `loadModelFromAssets(context, "ggml-base.bin")`。

### 小结表

| 情况           | 模型              | 构建                 | 结果                         |
|----------------|-------------------|----------------------|------------------------------|
| 占位 so        | 无                | `useWhisper=false`   | 识别为空，Toast 提示失败     |
| 真实 so，无模型 | assets 无 ggml    | `useWhisper=true`    | 同上                         |
| 真实 so + 模型 | assets 有 ggml-tiny.bin | `useWhisper=true` | 长按说话，松手后出字         |

---

## 常见问题与解决方案

以下均为实际使用中遇到过的问题及对应解决办法。

### 1. 为什么还是会连接系统 / 提示「未选择语音识别服务」「绑定失败」？

**原因**：没有使用本库的 **android** 模块，或使用的是「占位 so」（未开启 Whisper），导致 `engine.isAvailable()` 为 false，应用回退到了系统 `SpeechRecognizer`；部分机型未配置或限制第三方调用，就会报上述错误。

**解决**：

- 依赖必须使用 **android** 子模块：`implementation("com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0")`（注意是 `:android:1.3.0`，不是仅 `1.3.0`）。
- 本库 `gradle.properties` 中设置 **`useWhisper=true`**，重新编译 android 模块，使 so 内包含真实 Whisper 引擎。
- 在应用里**优先使用本地引擎**：仅当 `!engine.isAvailable()` 时再回退系统识别。只要 .so 成功加载，就应走本地采集 + 本地识别，不请求系统语音服务。

### 2. 说完话一直转圈，要等很久才出字 / 识别很慢

**原因**：Whisper 在手机 CPU 上推理几秒音频可能需要约 10–30 秒，属正常现象；若未做限长，录音过长会等更久。

**解决**：

- 本库已对送入识别的音频做**前 15 秒限长**，并提高推理线程数（如 4 线程），以缩短单次等待。
- 应用侧在「识别中」时显示 **「识别中，请稍候…」** 等提示，避免用户误以为卡死。
- 若仍觉慢，可考虑使用更小模型（如已用 tiny），或后续做流式/分段识别优化。

### 3. 长按时界面卡住几秒 / 模型加载导致 ANR

**原因**：在**主线程**调用 `loadModelFromAssets()` 或首次加载模型，会阻塞 UI。

**解决**：

- **不要在** 按键或弹窗显示时于主线程调用 `loadModelFromAssets()`。
- 在**后台线程**加载模型；若未加载完成就长按，可先显示「加载模型中…」，加载完成后再开始录音。
- 建议在输入法首次显示（如 `onStartInputView`）时于**后台**预加载一次模型，这样多数情况下长按时模型已就绪。

### 4. 识别结果为空 / Toast「没有识别到任何声音」或「识别失败」

**可能原因与对应办法**：

- **未放入模型**：在应用的 `app/src/main/assets/` 下放入 `ggml-tiny.bin`（或你指定的文件名），并确保调用了 `loadModelFromAssets(context)`。
- **未启用 Whisper 构建**：本库 `gradle.properties` 中需 `useWhisper=true`，否则 so 为占位实现，恒返回空。
- **录音过短或 PCM 为空**：确保在松手前有持续说话，且麦克风权限已授予；可打日志确认 `pcm` 非空且长度合理。
- **模型与 so 不匹配**：若曾改过 whisper 版本或构建方式，请用与当前 so 一致的模型（如官方 ggml-tiny.bin）。

### 5. JitPack 构建失败 / 找不到 android 模块

- 使用依赖时写全：`com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0`。
- 仓库需包含 **android** 子模块并推送到 GitHub；JitPack 会识别并构建根模块与 android 模块，生成带 .so 的 AAR。

### 6. 本地开发：如何用源码依赖（includeBuild）调试

在应用工程的 `settings.gradle.kts` 中：

```kotlin
includeBuild("../mengchuangjianghe-asr")
```

应用 `build.gradle.kts` 中依赖保持不变：`implementation("com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0")`。  
这样会使用本地 ASR 工程；本库需配置好 `sdk.dir`（如 `local.properties`）和 NDK，且 `useWhisper=true` 时首次构建会拉取 whisper.cpp。

---

## 本地构建

- **仅 JVM（根模块）**：`./gradlew build`（无需 Android 环境）。
- **含 Android 模块**：配置 `local.properties` 中 `sdk.dir` 及 NDK，然后：
  ```bash
  ./gradlew :android:assembleRelease
  ```
  产物在 `android/build/outputs/aar/`，内含各 ABI 的 `libmengchuangjianghe_asr_native.so`。

---

## 版本与发布

- 版本在根目录 **build.gradle.kts** 的 `version` 中指定（如 `1.3.0`）。
- 打 tag（如 `v1.3.0`）并推送到 GitHub 后，[JitPack](https://jitpack.io/#Mencaje/mengchuangjianghe-asr) 会自动构建；Android 应用使用 `com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0` 拉取带 .so 的 AAR。

---

## 其他用法（JVM）

- **纯本地可执行文件**：`AsrFactory.createWhisper(modelPath, executablePath)`，需自行部署 whisper.cpp 的 `main` 与 ggml 模型。
- **仅集成测试**：`AsrFactory.createDemo()`（返回固定示例文本）。
- **自建 HTTP 接口**：`AsrFactory.createHttp(apiUrl = "...", apiKey = "...")`（非本库算法）。

---

## License

Apache-2.0。本库使用的 Whisper 相关组件见 [NOTICE](NOTICE)。
