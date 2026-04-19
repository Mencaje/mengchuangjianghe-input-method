cmake_minimum_required(VERSION 3.22.1)
project("mengchuangjianghe_asr_native")

# 语音转文字 1.0：USE_WHISPER=ON 时用 FetchContent 拉取并编译 whisper.cpp，无需预编译
if(USE_WHISPER)
  set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
  set(WHISPER_BUILD_TESTS OFF CACHE BOOL "" FORCE)
  set(WHISPER_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
  include(FetchContent)
  FetchContent_Declare(whisper_cpp
    GIT_REPOSITORY https://github.com/ggml-org/whisper.cpp
    GIT_TAG v1.8.3
    GIT_SUBMODULES "ggml"
    GIT_SHALLOW TRUE
  )
  FetchContent_MakeAvailable(whisper_cpp)
endif()

add_library(mengchuangjianghe_asr_native SHARED whisper_jni.cpp)
find_library(log-lib log)
target_link_libraries(mengchuangjianghe_asr_native android ${log-lib})

if(USE_WHISPER)
  target_compile_definitions(mengchuangjianghe_asr_native PRIVATE USE_WHISPER=1)
  target_include_directories(mengchuangjianghe_asr_native PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${whisper_cpp_SOURCE_DIR}/include
  )
  target_link_libraries(mengchuangjianghe_asr_native whisper)
endif()
