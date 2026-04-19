将 Android 版预编译动态库放到对应 ABI 子目录，例如：
  arm64-v8a/librime.so
  armeabi-v7a/librime.so
（若官方构建还依赖 libopencc.so、libc++_shared.so 等，一并放入同名目录，打包时会自动进 APK。）

CMake 检测到 librime.so 后会编译「真实 JNI」并链接该库；否则仍为 STUB。

开源共建：若你已在本地放入合法来源的 .so，欢迎一并提交到仓库，便于他人克隆即可链接完整 Rime（请自行核对第三方库的许可证）。

获取 .so 的常见方式：
  1）自行用 NDK 交叉编译 librime（见 third_party/librime）；
  2）从同文输入法 Trime 等开源 APK 中解压 lib/<abi>/ 下与 rime/opencc 相关的 .so（注意许可证与 ABI 匹配）；
  3）使用社区「预编译 jniLibs」脚本（自行甄别来源）。

详细步骤与词库部署见仓库 doc/RIME.md。
