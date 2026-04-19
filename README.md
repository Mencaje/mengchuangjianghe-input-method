# 萌创匠盒输入法（孟创江河）· 开源安卓输入法

**仓库**：[github.com/Mencaje/mengchuangjianghe-input-method](https://github.com/Mencaje/mengchuangjianghe-input-method)  
**协议**：Apache License 2.0（见根目录 [`LICENSE`](LICENSE)）

面向 **社区共建**：欢迎改词库、修 Bug、加功能、提 PR。单靠个人维护很难做成「大家都好用」的输入法，开源就是为了让大家一起把它养大。

---

## 如何把说明同步到 GitHub（很重要）

文档和代码都在本仓库里；**只有你执行推送后**，GitHub 网页上才会出现最新的 `README.md`、最新代码。

在项目根目录（含 `.git` 的那一层）打开终端，执行：

```bash
git pull origin main
git push origin main
```

若提示登录，用 GitHub 账号或 **Personal Access Token**（Settings → Developer settings → Tokens）作为密码。  
如果你从未推送过含 `README.md` 的那次提交，本地可先执行 `git status` 确认有未推送提交，再 `git push`。

---

## 克隆后怎么用 Android Studio 打开

```bash
git clone https://github.com/Mencaje/mengchuangjianghe-input-method.git
cd mengchuangjianghe-input-method
```

用 **Android Studio** 打开 **`mengbox_input_android`** 文件夹（里面有 `settings.gradle.kts`、`app/`）。  
不要只打开仓库根目录下的某个子 `app`，否则 Gradle 找不到与 **`mengchuangjianghe-asr`** 的 `includeBuild` 联动。

要求：JDK 17、Android SDK；首次需能访问 Google Maven（或自行配置镜像）。

---

## 仓库里主要有什么

| 路径 | 内容 |
|------|------|
| **`mengbox_input_android/`** | 输入法主工程：UI、词库、JNI、Rime 接入等 |
| **`mengchuangjianghe-asr/`** | 语音相关（长按空格等），与主工程并列，由 Gradle 关联 |
| **`wordlist-public/`** | 公共词库源文件与构建脚本 |
| 其他如 `repo_deploy/`、`萌创匠盒输入法/`、`asr_deploy/` | 历史或部署参考，可按需浏览 |

---

## 目前已实现的能力（概括）

### 输入与界面

- **26 键**：中文拼音 / 英文、Shift 大写、候选栏、拼音行、部分场景 **Rime 预编辑**（方案就绪时）。
- **9 键（T9）**：数字缓冲、词库检索、候选与引导展示。
- **手写 / 笔画**：独立键盘布局，与统一候选区配合。
- **键盘切换**：候选区入口切换 9/26/手写/笔画；剪贴板浮层；与多款应用协作时的特殊处理（如个别 App 图标上屏策略）。
- **用户词与记忆**：`UserMemory` 等偏好记录。
- **远程词库 / 皮肤**：可从配置的 URL 拉取词表与皮肤资源（见工程内 `RemoteWordListFetcher`、`RemoteSkinFetcher` 等）。

### 智能与词库

- **本地大词表**：`assets` 下多类拼音词表、分类词表；脚本可合并、去重、生成统计权重等。
- **librime（Rime）接入**：JNI 层支持初始化、取候选、翻页、选词、预编辑、`get_input` 与本地缓冲对齐；**assets 内已带朙月拼音 + prelude + essay + stroke 等共享数据**（体积较大，属正常开源内容）。
- **未放置 `librime.so` 时**：走 JNI **STUB**，仍可编译运行，智能排序主要依赖内置词表与本地逻辑；放置官方/自编译 **`librime.so`**（及可能依赖的 **opencc** 等）后，可启用完整 Rime 解码（详见 `mengbox_input_android/doc/RIME.md`、`app/src/main/jniLibs/README.txt`）。

### 语音

- **长按空格**：可走 **本地 Whisper 类引擎**（`.so` + 模型），失败时可回退 **系统语音识别**（依设备与权限而定）。
- **语音模型 `.bin`** 体积大，一般不强制放进 Git；按 `mengbox_input_android/scripts/README_voice.md` 下载后放入 `assets` 即可。

---

## 尚未实现或明显不完整的地方（诚实清单）

以下内容 **不代表永远不做**，而是当前版本读者应心里有数：

| 类别 | 说明 |
|------|------|
| **云端大模型联想** | 未内置类似商业输入法的大规模云联想 / 热搜词云；侧重本地 + 可配置远程词库。 |
| **商业级运营能力** | 无完整「皮肤商店 / 账号体系 / 付费增值」闭环；皮肤与词库偏社区文件与 URL 分发。 |
| **librime 二进制** | **仓库不强制包含** `librime.so`（避免体积与许可证分发责任）；需要贡献者自备或从合规来源放入 `jniLibs` 后构建。 |
| **极致机型适配** | 折叠屏、平板分栏、横屏游戏键盘等未宣称「全机型满分体验」。 |
| **细节功能** | 例如部分键盘上的「数字键盘」等入口可能仍为占位或简化实现，以仓库内代码为准。 |

---

## 和主流输入法相比：优点与短板

### 优点

- **源码与词库构建流程开放**：可审计、可 Fork、可定制词库与行为，适合学习与二次发行（遵守各依赖许可证）。
- **架构上同时支持「传统本地词库」与「Rime 引擎」**：长句场景可交给 Rime + essay，小众词可用本地 TXT 合并补齐。
- **隐私取向**：可不依赖云端输入（取决于你是否启用远程 URL、是否使用系统语音）；本地 Whisper 路径可减少对系统语音的依赖（需自备模型）。
- **社区扩展**：词库、皮肤、脚本均可 PR；符合「大家一起维护」的目标。

### 短板（相对搜狗 / 讯飞 / Gboard 等产品）

- **投入与数据规模**：大厂有专职团队与海量用户反馈数据；本项目依赖社区贡献，默认体验会因词库与是否启用 Rime **差异很大**。
- **智能上限**：没有默认绑定的「无限云联想」；完整拼音句子上屏体验强依赖 **是否部署 Rime `.so` + 共享数据** 与词库维护。
- **语音体验**：依赖模型大小、设备算力、麦克风权限；与深度定制云语音的产品相比，「开箱即顶尖识别率」不现实。

---

## 我们希望把它发展成什么样的输入法

短期与中期方向（欢迎认领任务）：

1. **词库共建**：持续合并 `wordlist-public` 与 `assets` 词表，建立清晰的贡献规范（格式、许可、去重规则）。
2. **Rime 一体化体验**：文档化「一键放入 jniLibs + 方案」；可选提供 CI 或脚本生成最小可运行包（在许可证允许范围内）。
3. **稳定性与无障碍**：候选栏、焦点、深色模式、TalkBack 等逐步打磨。
4. **语音**：优化本地模型下载与首次引导；可选多种引擎插件化。
5. **皮肤与主题**：完善远程皮肤协议与缓存，鼓励社区上传合规皮肤。

长期愿景：**成为「可自主掌控数据流、可深度定制」的开源中文输入法基座**——学校、企业、极客群体可以 fork 后做自己的词库与策略，而不必完全依赖闭源云端。

---

## 参与贡献

- **词库**：改 `wordlist-public/` 或 `mengbox_input_android/app/src/main/assets/` 下源文件，跑通构建脚本后提 PR。
- **功能 / Bug**：改 `mengbox_input_android` 或 `mengchuangjianghe-asr`，PR 里写清复现步骤、截图或日志。
- **大文件**：`librime.so`、Whisper 模型等若需入库，请确认许可证与体积；必要时用 Git LFS 或 Release 附件分发。

---

## 许可证与第三方

- 本仓库默认 **Apache 2.0**。
- **librime**、**Rime 方案数据**、**Whisper 模型** 等第三方各有许可证，复制与再分发前请阅读对应目录或上游说明（如 `mengbox_input_android/third_party/librime/LICENSE`、`NOTICE`）。
