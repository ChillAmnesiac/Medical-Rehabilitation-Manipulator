# Add project specific ProGuard rules here.
-keep class org.rajawali3d.** { *; }
-keep class org.tensorflow.** { *; }
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
