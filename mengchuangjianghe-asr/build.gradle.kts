buildscript {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.10.1")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.0.21")
    }
}

plugins {
    id("java-library")
    id("org.jetbrains.kotlin.jvm") version "2.0.21"
}

subprojects {
    if (name == "android") {
        apply(plugin = "com.android.library")
        apply(plugin = "org.jetbrains.kotlin.android")
    }
}

group = "com.github.Mencaje"
version = "1.3.0"

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

repositories {
    google()
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib:2.0.21")
    testImplementation("junit:junit:4.13.2")
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
    kotlinOptions.jvmTarget = "11"
}

tasks.jar {
    manifest {
        attributes(
            "Implementation-Title" to "mengchuangjianghe-asr",
            "Implementation-Version" to version
        )
    }
}
