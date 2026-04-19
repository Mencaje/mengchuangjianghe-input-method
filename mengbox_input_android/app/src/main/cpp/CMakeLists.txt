# JNI：若存在预编译 librime（见 app/src/main/jniLibs/<abi>/librime.so），则链接真实引擎；
# 否则编译 STUB，便于无二进制时仍能打包。
cmake_minimum_required(VERSION 3.18)
project(rime_jni)
set(CMAKE_CXX_STANDARD 17)

set(LIBRIME_SO "${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/librime.so")

if (EXISTS "${LIBRIME_SO}")
    message(STATUS "HAVE_LIBRIME: ${LIBRIME_SO}")
    add_library(rime SHARED IMPORTED GLOBAL)
    set_target_properties(rime PROPERTIES IMPORTED_LOCATION "${LIBRIME_SO}")

    add_library(rime_jni SHARED rime_jni.cpp)
    target_compile_definitions(rime_jni PRIVATE HAVE_LIBRIME=1)
    target_include_directories(rime_jni PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/../../../../third_party/librime/src")
    find_library(log-lib log)
    target_link_libraries(rime_jni rime ${log-lib})
else ()
    message(STATUS "STUB JNI (place librime.so under src/main/jniLibs/${ANDROID_ABI}/ to enable)")
    add_library(rime_jni SHARED rime_jni.cpp)
    target_compile_definitions(rime_jni PRIVATE RIME_JNI_STUB=1)
    find_library(log-lib log)
    target_link_libraries(rime_jni ${log-lib})
endif ()
