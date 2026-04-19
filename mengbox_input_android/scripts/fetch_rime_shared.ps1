# 在本机更新 assets/rime_shared（走 jsDelivr，避免直连 GitHub 失败）
$ErrorActionPreference = "Stop"
$Base = Join-Path $PSScriptRoot "..\app\src\main\assets\rime_shared" | Resolve-Path
$Gh = "https://cdn.jsdelivr.net/gh"
# 不覆盖 default.yaml / luna_pinyin.schema.yaml（仓库内为移动端裁剪版）
$Map = @{
  "key_bindings.yaml"         = "$Gh/rime/rime-prelude@master/key_bindings.yaml"
  "punctuation.yaml"          = "$Gh/rime/rime-prelude@master/punctuation.yaml"
  "symbols.yaml"              = "$Gh/rime/rime-prelude@master/symbols.yaml"
  "pinyin.yaml"               = "$Gh/rime/rime-luna-pinyin@master/pinyin.yaml"
  "luna_pinyin.dict.yaml"     = "$Gh/rime/rime-luna-pinyin@master/luna_pinyin.dict.yaml"
  "essay.txt"                 = "$Gh/rime/rime-essay@master/essay.txt"
  "stroke.schema.yaml"        = "$Gh/rime/rime-stroke@master/stroke.schema.yaml"
  "stroke.dict.yaml"          = "$Gh/rime/rime-stroke@master/stroke.dict.yaml"
}
foreach ($name in $Map.Keys) {
  $uri = $Map[$name]
  $out = Join-Path $Base $name
  Write-Host "GET $name"
  Invoke-WebRequest -Uri $uri -OutFile $out -TimeoutSec 600 -UseBasicParsing
}
Write-Host "Done -> $Base"
Write-Host "未覆盖: default.yaml、luna_pinyin.schema.yaml（移动端裁剪）。若需官方完整版请自行从上游拷贝并处理 grammar patch。"
