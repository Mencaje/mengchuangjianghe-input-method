// 插件由根项目 buildscript + subprojects 应用

group = rootProject.group.toString()
version = rootProject.version.toString()

android {
    namespace = "com.mengchuangjianghe.asr.android"
    compileSdk = 34
    ndkVersion = "27.0.12077973"

    defaultConfig {
        minSdk = 24
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86", "x86_64")
        }
        externalNativeBuild {
            cmake {
                cppFlags += "-std=c++17"
                val useWhisper = project.findProperty("useWhisper") == "true"
                arguments += "-DUSE_WHISPER=${if (useWhisper) "ON" else "OFF"}"
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = "11"
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }
}

repositories {
    google()
    mavenCentral()
}

dependencies {
    api(project(":"))
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("org.jetbrains.kotlin:kotlin-stdlib:2.0.21")
}
