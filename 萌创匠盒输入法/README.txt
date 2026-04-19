本文件夹 = 萌创匠盒输入法官网/静态托管用，不要放进 APK 工程（mengbox_input_android）里。
用途：部署到静态托管平台后，作为官网介绍页；APK 通过网络拉取皮肤列表（skins/list.json、壁纸图片）。词库（wordlist.txt / wordlist.js）已迁至同目录下的 wordlist-public 文件夹，可单独拿到 GitHub 开源、供所有人一起维护；APK 拉取词库时请指向 wordlist-public 部署后的 URL（如 GitHub Pages 或其它静态托管）。

文件夹说明：
- index.html          官网介绍页
- build_skins.py      仅生成皮肤列表与白色壁纸（运行后生成 skins/list.json、skins/white/）
- skins/list.json     皮肤列表（名称、预览图与背景图 URL），由 build_skins.py 生成
- skins/white/        白色壁纸（preview.png、background.png），由 build_skins.py 生成
- skins/README.txt        皮肤图片尺寸与适配说明（preview 160×80，background 720×320；须适配四种键盘与底部横条）
- skins/皮肤制作教程.txt  做新皮肤必读：一个皮肤一个文件夹、两个子文件夹（键盘图片 / 介绍）、按键命名、双脚本用法
- skins/build_skin.py     单皮肤脚本：复制到「某个皮肤文件夹」内，与 intro、assets 同级，双击运行后生成该皮肤的 skin.json 与 intro.json

词库（已迁出）：
- 词库源文件、构建脚本与生成的 wordlist.txt / wordlist.js 均在上一级目录的 wordlist-public 文件夹中；该文件夹可单独开源到 GitHub，贡献者编辑 wordlist_src*.txt 后运行 python build.py 即可生成词库，供输入法拉取。

使用步骤：
1. 皮肤：运行 build_skins.py 会生成 skins/list.json 与 skins/white/ 白色壁纸，并扫描所有皮肤子文件夹（一个文件夹 = 一个皮肤，文件夹名 = 皮肤名），应用内两列一排展示。
2. 做新皮肤：看 skins/皮肤制作教程.txt；在 skins 下新建「皮肤名」文件夹，里放 intro（介绍）、assets（键盘图片：background、k26、k9、handwrite、stroke），把 skins/build_skin.py 复制进该文件夹后双击运行，再回到本根目录双击 build_skins.py 即被扫描进 list.json。
3. 把本文件夹（官网）上传到静态托管平台；词库请单独部署 wordlist-public（如 GitHub Pages），APK 拉取皮肤从本站、拉取词库从 wordlist-public 的 URL。

APK 不内置任何皮肤/壁纸，皮肤从本静态站拉取，词库从 wordlist-public 部署地址拉取。
