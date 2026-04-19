内置数据来自官方仓库：rime-prelude、rime-luna-pinyin、rime-essay、rime-stroke（经 jsDelivr 拉取）。
default.yaml 已裁剪为仅含 luna_pinyin；luna_pinyin.schema.yaml 已去掉 grammar:/hant 以免缺文件。
更新：运行 scripts/fetch_rime_shared.ps1 后，请重新应用 schema 裁剪或从本仓库 git 还原上述两处修改。
