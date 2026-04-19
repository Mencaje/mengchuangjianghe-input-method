# 萌创匠盒输入法 · 开源共建

本仓库目标：**任何人克隆后，用 Android Studio 即可打开、编译、参与改进**——词库、代码、脚本全部公开，欢迎一起维护。

## 一键上手（给贡献者）

1. **克隆**

   ```bash
   git clone https://github.com/Mencaje/mengchuangjianghe-input-method.git
   cd mengchuangjianghe-input-method
   ```

2. **用 Android Studio 打开工程目录**

   请打开 **`mengbox_input_android`** 这一层文件夹（内含 `settings.gradle.kts`、`app/`），不要只打开仓库根目录里的单个 `app`。  
   根目录下的 `mengchuangjianghe-asr` 与输入法通过 Gradle `includeBuild` 联动，需与 `mengbox_input_android` **并列存在**（克隆本仓库即可）。

3. **同步 Gradle、选设备、运行**

   - 安装 JDK 17（或 Android Studio 自带 JDK）。
   - 首次 Sync 失败时，检查网络能否访问 Google Maven（必要时配置镜像）。

## 仓库里有什么

| 路径 | 说明 |
|------|------|
| `mengbox_input_android/` | **输入法 Android 主工程**（26 键 / 9 键 / 手写 / 笔画、词库、Rime 接入等） |
| `mengchuangjianghe-asr/` | 语音识别相关本地库（长按空格说话等），与主工程并列 |
| `wordlist-public/` | 公共词库源文件与构建脚本 |
| `萌创匠盒输入法/`、`repo_deploy/`、`asr_deploy/` | 历史或部署用目录，可按需参考 |

## 可选组件（增强体验，非克隆必需）

- **完整 librime**：将 `librime.so`（及依赖的 `libopencc.so` 等）放入 `mengbox_input_android/app/src/main/jniLibs/<abi>/`。  
  未放置时仍可编译运行（JNI STUB），智能程度依赖内置数据与本地词库。详见 `mengbox_input_android/app/src/main/jniLibs/README.txt`、`mengbox_input_android/doc/RIME.md`。
- **语音模型**：Whisper 等 `.bin` 体积大，默认不强制入库；可按 `mengbox_input_android/scripts/README_voice.md` 下载后放入 `assets`。

## 共建方式

- **改词库**：编辑 `wordlist-public/` 或 `app/src/main/assets/` 下词表与脚本，说明改动点后发 Pull Request。
- **改功能 / 修 Bug**：直接改 `mengbox_input_android` 或 ASR 模块，PR 描述复现步骤与测试结果。

## 许可证

仓库根目录 [`LICENSE`](LICENSE) 为 **Apache License 2.0**。第三方组件（如 `third_party/librime`）以其自带许可证为准，见各自目录。
