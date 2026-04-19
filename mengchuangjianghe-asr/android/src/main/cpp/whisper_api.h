/**
 * 最小 whisper C API 声明，与 whisper.cpp 的 whisper.h 兼容。
 * 接入真实 whisper.cpp 时由 third_party 提供实现，此处仅声明以便 JNI 编译。
 * 参见 https://github.com/ggml-org/whisper.cpp
 */
#ifndef MENGCHUANGJIANGHE_WHISPER_API_H
#define MENGCHUANGJIANGHE_WHISPER_API_H

#ifdef __cplusplus
extern "C" {
#endif

struct whisper_context;
struct whisper_full_params;

typedef struct whisper_context whisper_context;
typedef struct whisper_full_params whisper_full_params;

typedef int whisper_sampling_strategy;
enum {
    WHISPER_SAMPLING_GREEDY = 0,
    WHISPER_SAMPLING_BEAM_SEARCH = 1,
};

/** 从文件路径加载模型，返回 context，失败返回 NULL */
whisper_context *whisper_init_from_file(const char *path);

void whisper_free(whisper_context *ctx);

/** 默认推理参数 */
whisper_full_params whisper_full_default_params(whisper_sampling_strategy strategy);

/** 对 float  PCM (16kHz mono) 做识别，返回 0 成功 */
int whisper_full(whisper_context *ctx, whisper_full_params params, const float *samples, int n_samples);

int whisper_full_n_segments(whisper_context *ctx);

/** 取第 i 段文本，i 从 0 到 n_segments-1 */
const char *whisper_full_get_segment_text(whisper_context *ctx, int i);

#ifdef __cplusplus
}
#endif

#endif
