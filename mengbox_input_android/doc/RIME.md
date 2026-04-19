# librime（Rime）完全接入说明

[librime](https://github.com/rime/librime) 使用 **BSD 3-Clause**，完整许可证见 `third_party/librime/LICENSE`。请在仓库 `NOTICE` 中保留第三方声明。

## 行为说明（与你关心的「聪明组词」）

- **未放置 `librime.so`**：CMake 编译 **STUB JNI**，`RimeEngine.isReady()` 为 false，26 键拼音仍使用原有 **PinyinDict + 合并词库**。
- **已放置 `librime.so` 且初始化成功**：`RimeEngine.isReady()` 为 true。`getPinyinCandidates` 会先取 **Rime**（引擎 + **方案自带词库**，由 plum/雾凇等部署，一般已很丰富），再 **拼接本地 txt 词库独有候选**（去重、Rime 优先）。这样：**长句、常用说法靠 Rime**；**你们自维护、垂直领域词条**仍能补上，避免「只开一头、另一头全灰」。
- **Rime 本条无候选**：仅用本地路径，行为与未集成 Rime 时一致。
- **接续字 boost**（`boostCandidatesWithAssociation`）：**Rime 未就绪**时对整表候选生效；**Rime 就绪**时仅在缓冲为 **单个完整音节**（如先上屏「美」再仅输入 `li`）时对 **Rime 与本地合并后的列表** 再排序，并把该栏 **Rime 菜单下标对齐关闭**（改按候选文字上屏），避免「美 + li」因 Rime 单字序把「力」排在「丽」前。

## 一步：放入预编译 librime

在 **`app/src/main/jniLibs/<abi>/librime.so`** 放置与目标 ABI 一致的动态库（至少 arm64-v8a / armeabi-v7a）。

可从以下来源获取（自行核对许可证与兼容性）：

1. **自行交叉编译** `third_party/librime`（依赖 Boost、yaml-cpp、marisa、leveldb、opencc 等，随版本变化）。
2. **从 Trime 等开源 APK** 解压 `lib/<abi>/` 下 `librime.so` / `libopencc.so` / `libc++_shared.so`（若缺则一并拷贝到同一 `jniLibs/<abi>/`）。
3. 其它社区提供的 Android 预编译包（自行甄别）。

重新 Sync + 编译后，Gradle CMake 会检测到文件并 **链接真实 JNI**（log 中可见 `HAVE_LIBRIME`）。

## 二步：部署 Rime 共享数据（方案 + 词典编译产物）

仅有 `librime.so` **不够**，还需要 Rime **数据目录**。推荐：

1. 在本机用 [plum](https://github.com/rime/plum) 安装 **`luna-pinyin`**、**`prelude`**（以及下文清单中的依赖），将 **部署输出目录里的全部内容** 拷入 **`app/src/main/assets/rime_shared/`**（保持相对路径；首启会复制到应用私有目录 `rime/share`，见 `RimeEngine`）。

2. 或复制本机已安装 Rime 的同步目录（如 Windows：`%AppData%/Rime`；macOS：`~/Library/Rime`）下对应文件；体积大时可只拷清单内条目 + 分包/按需下载。

首次启动后 JNI 会执行 `initialize` + `start_maintenance`（可生成 `build/*.bin`）。若仍无候选，检查 logcat `rime` / `rime_jni`，确认 `shared_data_dir` 下方案与词典是否齐全、编译是否成功。

### 最小文件清单（plum：`prelude` + `luna-pinyin`）

下列文件名以官方 plum 配方为准；若某版本改名，以你本机 plum 安装后的实际文件为准。**原则：schema 里 `import_tables` / `__include` 链上的 yaml、txt、dict 都要在 assets 里有一份。**

| 类别 | 常见文件名 | 说明 |
|------|------------|------|
| 全局 | `default.yaml` | prelude 提供；默认配置入口 |
| 标点/按键 | `key_bindings.yaml`、`punctuation.yaml`、`symbols.yaml` | prelude，符号与标点 |
| 语言模型 | `essay.txt` | 常用词频与组词统计，**强烈建议带上**，否则整体排序偏「呆」 |
| 朙月拼音 | `luna_pinyin.schema.yaml`、`luna_pinyin.dict.yaml` | 方案主文件与主词典 |
| 依赖表 | `stroke.dict.yaml` 等 | `luna_pinyin` 常引用笔画反查等表；**缺哪个看 `luna_pinyin.schema.yaml` / `luna_pinyin.dict.yaml` 里的 `import_tables` / `import_preset`** |
| 简体（可选） | `opencc/` 下转换配置 | 若方案启用 OpenCC 简繁，需连同 opencc 数据一并放入（缺则相关选项可能无效） |
| 编译产物（可选但省心） | `build/*.bin` | 在本机 Rime 已部署并成功编译后，把 `build` 目录一并拷入，可减少首启编译时间、降低设备上编译失败概率 |

**自检命令（开发机已装 Rime 时）：** 在同步目录执行全文搜索 `luna_pinyin`，确认没有指向缺失路径的 `import`。

### 若改用雾凇等第三方方案（如 rime-ice）

- 以该仓库 / 发行包的 **README 与文件列表** 为准，通常除方案 yaml、dict 外还有扩展词库子表。
- JNI 里当前写死 `select_schema(..., "luna_pinyin")`，改用雾凇时需把 `app/src/main/cpp/rime_jni.cpp` 中的 **schema id** 改成对方方案名（如部分发行版为 `rime_ice`），并重新编译。

## 方案 ID

JNI 默认 `select_schema(..., "luna_pinyin")`。若你使用雾凇等其它方案，请改 `app/src/main/cpp/rime_jni.cpp` 中 schema 字符串并重新编译。

## 这不是「零配置魔法」

Rime **仍然依赖语言数据与统计模型**；区别是这些数据由 **Rime 社区方案**维护，而不是你在仓库里无限堆 TXT。完全覆盖人类所有说法仍不现实，但比纯手写词表通用得多。
