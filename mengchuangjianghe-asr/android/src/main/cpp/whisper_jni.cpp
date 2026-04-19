#include <jni.h>
#include <string>
#include <cstring>
#include <vector>
#include <android/log.h>

#define LOG_TAG "WhisperJNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

#ifdef USE_WHISPER
// 使用预编译目录下的 whisper.h，与 libwhisper.a 一致
#include "whisper.h"
#endif

static const int kExpectedSampleRate = 16000;

extern "C" {

#ifdef USE_WHISPER
static whisper_context* s_whisper_ctx = nullptr;
#endif

// 从 Java 传入的模型路径加载模型（仅 USE_WHISPER 时有效）
JNIEXPORT jboolean JNICALL
Java_com_mengchuangjianghe_asr_android_WhisperNative_nativeLoadModel(
    JNIEnv* env,
    jclass clazz,
    jstring model_path) {
#ifdef USE_WHISPER
    if (!model_path) return JNI_FALSE;
    const char* path = env->GetStringUTFChars(model_path, nullptr);
    if (!path) return JNI_FALSE;
    if (s_whisper_ctx) {
        whisper_free(s_whisper_ctx);
        s_whisper_ctx = nullptr;
    }
    struct whisper_context_params cparams = whisper_context_default_params();
    s_whisper_ctx = whisper_init_from_file_with_params(path, cparams);
    if (s_whisper_ctx) {
        LOGI("whisper model loaded");
        env->ReleaseStringUTFChars(model_path, path);
        return JNI_TRUE;
    }
    LOGE("whisper_init_from_file failed");
    env->ReleaseStringUTFChars(model_path, path);
    return JNI_FALSE;
#else
    (void)env;
    (void)clazz;
    (void)model_path;
    return JNI_FALSE;
#endif
}

JNIEXPORT jstring JNICALL
Java_com_mengchuangjianghe_asr_android_WhisperNative_nativeRecognize(
    JNIEnv* env,
    jclass clazz,
    jbyteArray pcm_data,
    jint sample_rate) {

    if (!pcm_data || sample_rate <= 0) {
        return env->NewStringUTF("");
    }

    jsize len = env->GetArrayLength(pcm_data);
    if (len == 0) {
        return env->NewStringUTF("");
    }

#ifdef USE_WHISPER
    if (!s_whisper_ctx) {
        LOGE("nativeRecognize: model not loaded");
        return env->NewStringUTF("");
    }

    jbyte* pcm_bytes = env->GetByteArrayElements(pcm_data, nullptr);
    if (!pcm_bytes) return env->NewStringUTF("");

    // 16bit 小端 -> float [-1,1]，长度减半
    int num_samples = len / 2;
    std::vector<float> samples(num_samples);
    const int16_t* p = reinterpret_cast<const int16_t*>(pcm_bytes);
    for (int i = 0; i < num_samples; ++i) {
        samples[i] = p[i] / 32768.0f;
    }
    env->ReleaseByteArrayElements(pcm_data, pcm_bytes, JNI_ABORT);

    // 重采样：若输入不是 16kHz，此处简化处理（whisper 要求 16kHz）
    const float* data = samples.data();
    int n = num_samples;
    if (sample_rate != kExpectedSampleRate && sample_rate > 0) {
        // 简单线性重采样到 16kHz
        int out_count = (int)((int64_t)num_samples * kExpectedSampleRate / sample_rate);
        if (out_count > 0 && out_count <= num_samples * 2) {
            std::vector<float> resampled(out_count);
            for (int i = 0; i < out_count; ++i) {
                double src_idx = (double)i * sample_rate / kExpectedSampleRate;
                int i0 = (int)src_idx;
                int i1 = i0 + 1;
                if (i1 >= num_samples) i1 = num_samples - 1;
                float t = (float)(src_idx - i0);
                resampled[i] = samples[i0] * (1.f - t) + samples[i1] * t;
            }
            data = resampled.data();
            n = out_count;
        }
    }

    // 仅取前 15 秒音频，避免推理过久（手机 CPU 上 15s 约需 10–30s）
    const int max_samples = kExpectedSampleRate * 15;
    if (n > max_samples) n = max_samples;

    whisper_full_params params = whisper_full_default_params(WHISPER_SAMPLING_GREEDY);
    params.print_realtime = false;
    params.print_progress = false;
    params.print_timestamps = false;
    params.translate = false;
    params.language = "zh";
    params.n_threads = 4;

    int ret = whisper_full(s_whisper_ctx, params, data, n);
    if (ret != 0) {
        LOGE("whisper_full failed: %d", ret);
        return env->NewStringUTF("");
    }

    std::string text;
    int n_seg = whisper_full_n_segments(s_whisper_ctx);
    for (int i = 0; i < n_seg; ++i) {
        const char* seg = whisper_full_get_segment_text(s_whisper_ctx, i);
        if (seg) text += seg;
    }
    return env->NewStringUTF(text.c_str());
#else
    (void)len;
    (void)sample_rate;
    return env->NewStringUTF("");
#endif
}

JNIEXPORT jboolean JNICALL
Java_com_mengchuangjianghe_asr_android_WhisperNative_nativeIsModelLoaded(
    JNIEnv* env,
    jclass clazz) {
#ifdef USE_WHISPER
    (void)env;
    (void)clazz;
    return s_whisper_ctx != nullptr ? JNI_TRUE : JNI_FALSE;
#else
    (void)env;
    (void)clazz;
    return JNI_FALSE;
#endif
}

} // extern "C"
