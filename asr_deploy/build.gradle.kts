plugins {
    id("java-library")
    id("org.jetbrains.kotlin.jvm") version "1.9.22"
}

group = "com.github.Mencaje"
version = "1.3.0"

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.9.22")
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
