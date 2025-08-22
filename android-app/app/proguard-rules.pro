# Keep rules for Retrofit/Moshi (MVP — minify disabled in debug)
-dontwarn okio.**
-dontwarn javax.annotation.**
-keep class kotlin.Metadata { *; }
-keep class com.squareup.moshi.** { *; }
-keep class com.squareup.okhttp3.** { *; }
-keep class retrofit2.** { *; }
