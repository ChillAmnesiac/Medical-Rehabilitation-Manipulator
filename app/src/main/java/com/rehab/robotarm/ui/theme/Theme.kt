package com.rehab.robotarm.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// 赛博朋克暗黑主题
private val CyberDarkColorScheme = darkColorScheme(
    primary = CyberBlue,
    onPrimary = Color.Black,
    primaryContainer = CyberPurple,
    onPrimaryContainer = Color.White,

    secondary = CyberGreen,
    onSecondary = Color.Black,
    secondaryContainer = CyberOrange,
    onSecondaryContainer = Color.White,

    tertiary = CyberPink,
    onTertiary = Color.White,

    background = DarkBackground,
    onBackground = Color.White,

    surface = DarkSurface,
    onSurface = Color.White,

    surfaceVariant = DarkCard,
    onSurfaceVariant = CyberBlue,

    error = CyberPink,
    onError = Color.White
)

@Composable
fun RehabRobotArmTheme(
    darkTheme: Boolean = true,  // 强制使用暗黑主题
    content: @Composable () -> Unit
) {
    val colorScheme = CyberDarkColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = DarkBackground.toArgb()
            window.navigationBarColor = DarkBackground.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
