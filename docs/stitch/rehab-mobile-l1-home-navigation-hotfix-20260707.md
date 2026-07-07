# Rehab Mobile L1 Home Navigation Hotfix Stitch Prompt

请在 `rehab-arm-mobile-stitch` 的移动端首页补齐首屏动作导航，不改视觉风格，只补交互语义和可用性。

## 必须修复

1. 首页按钮 `查看康复师建议` 必须是可点击动作，点击后进入 `ai-plan.html`。
2. 首页按钮 `问康复师` 必须是可点击动作，点击后进入 `ai-plan.html`。
3. 推荐训练卡片右侧播放按钮必须是可点击动作，点击后进入 `device.html`，让用户先完成设备绑定/训练准备。
4. 所有这些动作都要保留 48px 以上可点击区域，移动端触摸体验不能变差。
5. 不要新增解释性文案，不要改变现有视觉层级，不要把首页改成营销页。

## 实现约束

- 给首页可点击控件增加稳定语义，例如 `data-nav-target="ai-plan.html"` / `data-nav-target="device.html"`。
- 页面加载后统一绑定 `[data-nav-target]` 点击事件，使用当前页面 URL 解析相对路径。
- 生成后的 `apps/web/public/rehab-arm-mobile/home.html` 和 `apps/mobile/rehab-arm-android/www/home.html` 必须保持同等交互。

## 验收

- 打开 `home.html` 后，点击 `问康复师` 会进入 `ai-plan.html`。
- 点击 `查看康复师建议` 会进入 `ai-plan.html`。
- 点击推荐训练播放按钮会进入 `device.html`。
- L1 前端 QA 不得再出现 `home_primary_action_navigation`、`home_ask_therapist_navigation`、`home_navigation_click_handler` 缺失。
