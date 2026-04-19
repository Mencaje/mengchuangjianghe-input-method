# 发布到 GitHub 与 JitPack 步骤

本文说明如何将本库（含语音转文字 1.0 与 Android 模块）发布到 [GitHub Mencaje/mengchuangjianghe-asr](https://github.com/Mencaje/mengchuangjianghe-asr)，并让 JitPack 可构建。

## 一、首次从本地推送到 GitHub

若当前目录**还不是** git 仓库：

```bash
cd mengchuangjianghe-asr
git init
git remote add origin https://github.com/Mencaje/mengchuangjianghe-asr.git
git add .
git commit -m "feat: 语音转文字 1.0 - 集成 whisper.cpp，Android .so 本地识别，不依赖系统语音服务"
git branch -M main
git push -u origin main
```

若本地已是克隆的仓库，只需在修改后：

```bash
git add .
git commit -m "docs: 完善 README 与常见问题；语音 1.0 跑通说明"
git push origin main
```

## 二、打 tag 以触发 JitPack 构建

版本号与根目录 `build.gradle.kts` 中 `version` 一致（如 `1.3.0`）：

```bash
git tag v1.3.0
git push origin v1.3.0
```

推送 tag 后，在 [JitPack 控制台](https://jitpack.io/#Mencaje/mengchuangjianghe-asr) 可查看构建日志。成功后，他人即可使用：

- `com.github.Mencaje:mengchuangjianghe-asr:1.3.0`（根模块 JAR）
- `com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0`（Android 带 .so 的 AAR）

## 三、提交前请确认

- `local.properties` 已在 `.gitignore` 中，不会提交 SDK 路径。
- 未提交 `android/src/main/cpp/whisper_prebuilt/`（若存在，属本地预编译，已忽略）。
- README、NOTICE、LICENSE 与版本号已按需更新。

## 四、常见问题（发布相关）

- **JitPack 构建 android 失败**：确保仓库中有 `android` 子模块目录及 `settings.gradle.kts` 中 `include(":android")`；且 `gradle-wrapper.properties` 中 Gradle 版本满足 Android Gradle Plugin 要求（如 8.11.1）。
- **依赖写 com.github.zxcvvvvvbnm**：组织已迁至 Mencaje，应使用 `com.github.Mencaje:mengchuangjianghe-asr:android:1.3.0`。
