/*
 * Rime JNI：STUB（无 librime.so）时可编译；HAVE_LIBRIME 时链接第三方预编译 librime。
 * simulate_key_sequence = 拼音方案下自动音节划分与解码；built-in 词库由部署的 YAML/词典决定。
 */
#include <jni.h>
#include <cstring>

#ifdef ANDROID
#include <android/log.h>
#else
#define __android_log_print(...)
#endif

#ifdef RIME_JNI_STUB

extern "C" JNIEXPORT jboolean JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeInit(JNIEnv *env, jclass clazz, jstring jshared,
                                                jstring juser) {
  (void)env;
  (void)clazz;
  (void)jshared;
  (void)juser;
  return JNI_FALSE;
}

extern "C" JNIEXPORT jobjectArray JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeUpdateAndGetCandidates(JNIEnv *env, jclass clazz,
                                                                  jstring jkeys) {
  (void)clazz;
  (void)jkeys;
  jclass stringClass = env->FindClass("java/lang/String");
  return env->NewObjectArray(0, stringClass, nullptr);
}

extern "C" JNIEXPORT jobjectArray JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeFlipCandidatePage(JNIEnv *env, jclass clazz,
                                                             jboolean backward) {
  (void)backward;
  jclass stringClass = env->FindClass("java/lang/String");
  return env->NewObjectArray(0, stringClass, nullptr);
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_mengchuangbox_input_RimeJni_nativePickCandidateOnCurrentPage(JNIEnv *env, jclass clazz,
                                                                      jint index) {
  (void)index;
  return nullptr;
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeGetPreedit(JNIEnv *env, jclass clazz) {
  jstring empty = env->NewStringUTF("");
  return empty;
}

extern "C" JNIEXPORT void JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeSetOption(JNIEnv *env, jclass clazz, jstring opt,
                                                     jboolean value) {
  (void)env;
  (void)clazz;
  (void)opt;
  (void)value;
}

extern "C" JNIEXPORT void JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeClearComposition(JNIEnv *env, jclass clazz) {
  (void)env;
  (void)clazz;
}

extern "C" JNIEXPORT jobjectArray JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeGetCurrentCandidates(JNIEnv *env, jclass clazz) {
  (void)clazz;
  jclass stringClass = env->FindClass("java/lang/String");
  return env->NewObjectArray(0, stringClass, nullptr);
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeGetInput(JNIEnv *env, jclass clazz) {
  (void)clazz;
  return env->NewStringUTF("");
}

extern "C" JNIEXPORT void JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeShutdown(JNIEnv *env, jclass clazz) {
  (void)env;
  (void)clazz;
}

#elif defined(HAVE_LIBRIME)

#include <rime_api.h>
#include <string>
#include <vector>

static RimeApi *g_api = nullptr;
static RimeSessionId g_session = 0;

static std::string jstring_to_utf8(JNIEnv *env, jstring js) {
  if (!js) return {};
  const char *c = env->GetStringUTFChars(js, nullptr);
  std::string s(c ? c : "");
  env->ReleaseStringUTFChars(js, c);
  return s;
}

static jobjectArray candidates_to_jarray(JNIEnv *env, jclass stringClass,
                                           const std::vector<std::string> &out) {
  jobjectArray arr = env->NewObjectArray(static_cast<jsize>(out.size()), stringClass, nullptr);
  for (size_t i = 0; i < out.size(); ++i) {
    jstring js = env->NewStringUTF(out[i].c_str());
    env->SetObjectArrayElement(arr, static_cast<jsize>(i), js);
    env->DeleteLocalRef(js);
  }
  return arr;
}

static jobjectArray menu_to_jarray(JNIEnv *env, RimeContext &ctx) {
  jclass stringClass = env->FindClass("java/lang/String");
  std::vector<std::string> out;
  RimeMenu &menu = ctx.menu;
  int n = menu.num_candidates;
  if (menu.candidates && n > 0) {
    for (int i = 0; i < n && i < 96; ++i) {
      const char *t = menu.candidates[i].text;
      if (t && *t) out.emplace_back(t);
    }
  }
  return candidates_to_jarray(env, stringClass, out);
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeInit(JNIEnv *env, jclass clazz, jstring jshared,
                                                jstring juser) {
  (void)clazz;
  if (g_session && g_api) {
    g_api->destroy_session(g_session);
    g_session = 0;
    g_api->finalize();
    g_api = nullptr;
  }
  RIME_STRUCT(RimeTraits, traits);
  static std::string shared_storage;
  static std::string user_storage;
  shared_storage = jstring_to_utf8(env, jshared);
  user_storage = jstring_to_utf8(env, juser);
  traits.shared_data_dir = shared_storage.c_str();
  traits.user_data_dir = user_storage.c_str();
  traits.app_name = "rime.mengbox";
  traits.min_log_level = 2;

  g_api = rime_get_api();
  if (!g_api) return JNI_FALSE;
  g_api->setup(&traits);
  g_api->initialize(&traits);
  if (g_api->start_maintenance(True)) {
    g_api->join_maintenance_thread();
  }
  g_session = g_api->create_session();
  if (!g_session) return JNI_FALSE;
  g_api->select_schema(g_session, "luna_pinyin");
  if (g_api->set_option != nullptr) {
    g_api->set_option(g_session, "simplification", True);
  }
  return JNI_TRUE;
}

extern "C" JNIEXPORT jobjectArray JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeUpdateAndGetCandidates(JNIEnv *env, jclass clazz,
                                                                  jstring jkeys) {
  (void)clazz;
  jclass stringClass = env->FindClass("java/lang/String");
  if (!g_api || !g_session) {
    return env->NewObjectArray(0, stringClass, nullptr);
  }
  std::string keys = jstring_to_utf8(env, jkeys);
  g_api->clear_composition(g_session);
  if (!keys.empty()) {
    if (!g_api->simulate_key_sequence(g_session, keys.c_str())) {
      return env->NewObjectArray(0, stringClass, nullptr);
    }
  }
  RIME_STRUCT(RimeContext, ctx);
  if (!g_api->get_context(g_session, &ctx)) {
    return env->NewObjectArray(0, stringClass, nullptr);
  }
  jobjectArray arr = menu_to_jarray(env, ctx);
  g_api->free_context(&ctx);
  return arr;
}

extern "C" JNIEXPORT jobjectArray JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeGetCurrentCandidates(JNIEnv *env, jclass clazz) {
  (void)clazz;
  jclass stringClass = env->FindClass("java/lang/String");
  if (!g_api || !g_session) {
    return env->NewObjectArray(0, stringClass, nullptr);
  }
  RIME_STRUCT(RimeContext, ctx);
  if (!g_api->get_context(g_session, &ctx)) {
    return env->NewObjectArray(0, stringClass, nullptr);
  }
  jobjectArray arr = menu_to_jarray(env, ctx);
  g_api->free_context(&ctx);
  return arr;
}

extern "C" JNIEXPORT jobjectArray JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeFlipCandidatePage(JNIEnv *env, jclass clazz,
                                                             jboolean backward) {
  (void)clazz;
  jclass stringClass = env->FindClass("java/lang/String");
  if (!g_api || !g_session) {
    return env->NewObjectArray(0, stringClass, nullptr);
  }
  g_api->change_page(g_session, backward ? True : False);
  RIME_STRUCT(RimeContext, ctx);
  if (!g_api->get_context(g_session, &ctx)) {
    return env->NewObjectArray(0, stringClass, nullptr);
  }
  jobjectArray arr = menu_to_jarray(env, ctx);
  g_api->free_context(&ctx);
  return arr;
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_mengchuangbox_input_RimeJni_nativePickCandidateOnCurrentPage(JNIEnv *env, jclass clazz,
                                                                      jint index) {
  (void)clazz;
  if (!g_api || !g_session || index < 0) return nullptr;
  if (!g_api->select_candidate_on_current_page(g_session, static_cast<size_t>(index))) {
    return nullptr;
  }
  RIME_STRUCT(RimeCommit, commit);
  std::string out;
  if (g_api->get_commit(g_session, &commit)) {
    if (commit.text) out = commit.text;
    g_api->free_commit(&commit);
    return env->NewStringUTF(out.c_str());
  }
  return env->NewStringUTF("");
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeGetPreedit(JNIEnv *env, jclass clazz) {
  (void)clazz;
  if (!g_api || !g_session) return env->NewStringUTF("");
  RIME_STRUCT(RimeContext, ctx);
  if (!g_api->get_context(g_session, &ctx)) return env->NewStringUTF("");
  std::string pre;
  if (ctx.composition.preedit) pre = ctx.composition.preedit;
  g_api->free_context(&ctx);
  return env->NewStringUTF(pre.c_str());
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeGetInput(JNIEnv *env, jclass clazz) {
  (void)clazz;
  if (!g_api || !g_session || !g_api->get_input) {
    return env->NewStringUTF("");
  }
  const char *s = g_api->get_input(g_session);
  return env->NewStringUTF(s ? s : "");
}

extern "C" JNIEXPORT void JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeSetOption(JNIEnv *env, jclass clazz, jstring opt,
                                                     jboolean value) {
  (void)clazz;
  if (!g_api || !g_session || !opt) return;
  std::string key = jstring_to_utf8(env, opt);
  if (key.empty()) return;
  g_api->set_option(g_session, key.c_str(), value ? True : False);
}

extern "C" JNIEXPORT void JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeClearComposition(JNIEnv *env, jclass clazz) {
  (void)env;
  (void)clazz;
  if (g_api && g_session) {
    g_api->clear_composition(g_session);
  }
}

extern "C" JNIEXPORT void JNICALL
Java_com_mengchuangbox_input_RimeJni_nativeShutdown(JNIEnv *env, jclass clazz) {
  (void)env;
  (void)clazz;
  if (g_api && g_session) {
    g_api->destroy_session(g_session);
    g_session = 0;
    g_api->finalize();
  }
  g_api = nullptr;
}

#endif
