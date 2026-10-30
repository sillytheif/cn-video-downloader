"""Friendly explanations; no access restriction circumvention."""
def friendly_error(detail: str) -> str:
    text = detail.lower()
    for words, message in [
        (('drm', 'copyright protection'), '此视频受 DRM 保护，无法下载；本工具不提供破解。'),
        (('vip', 'premium', 'members-only', 'sign in', 'login', 'log in', 'cookies', 'payment', '会员', '登录'), '此视频需要会员、付费或登录授权，当前版本不支持。'),
        (('geo', 'not available in your country', 'region', '地区'), '此视频存在地区限制，当前网络无法访问。'),
        (('unsupported url', 'no suitable extractor'), '暂不支持此链接，请确认是视频页面并尝试更新 yt-dlp。'),
        (('timed out', 'network', 'connection', 'resolve', 'http error', 'unable to download'), '网络连接失败或网站拒绝访问，请检查网络后重试。'),
        (('ffmpeg',), '视频合并失败，请检查 runtime 中的 ffmpeg.exe。'),
    ]:
        if any(word in text for word in words):
            return message
    return '下载失败，请查看下方日志；网站接口可能已变化。'
