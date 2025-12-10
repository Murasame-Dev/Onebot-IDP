"""
消息文本配置
集中管理所有机器人回复消息，便于修改和国际化
"""
import config

# ==================== 绑定相关 ====================

# /bind 命令在群聊中不带用户名时的提示
BIND_PRIVATE_ONLY = f"请在私聊中使用 {config.FULL_CMD_BIND} 命令，或使用 {config.FULL_CMD_BIND} <用户名> 指定要绑定的账号"

# 已经绑定过账号时的提示
BIND_ALREADY_BOUND = f"您已绑定账号: {{username}}\n如需重新绑定，请先使用 {config.FULL_CMD_UNBIND} 解绑"

# 已有进行中的绑定请求
BIND_REQUEST_EXISTS = f"您已有一个进行中的绑定请求\n请先完成或使用 {config.FULL_CMD_BIND_CANCEL} 取消当前请求"

# 取消绑定请求成功
BIND_CANCEL_SUCCESS = "✅ 已取消当前绑定请求"

# 没有进行中的绑定请求
BIND_CANCEL_NO_REQUEST = "❌ 您没有进行中的绑定请求"

# 绑定链接消息模板
BIND_LINK_MESSAGE = """请点击以下链接完成绑定验证:
{bind_url}

链接将在 {expire_minutes} 分钟后过期"""

# 绑定链接消息 - 指定用户名时的附加信息
BIND_LINK_EXPECTED_USER = "\n期望绑定的用户名: {username}"

# 绑定链接消息 - 未指定用户名时的附加信息
BIND_LINK_ANY_USER = "\n将绑定到登录的账号"


# ==================== 解绑相关 ====================

# 尚未绑定时解绑的提示
UNBIND_NOT_BOUND = "您尚未绑定任何账号"

# 解绑成功
UNBIND_SUCCESS = "已成功解绑账号: {username}"


# ==================== 状态查询相关 ====================

# 已绑定时的状态信息
STATUS_BOUND = """当前绑定状态:
用户名: {username}
绑定时间: {bound_time}"""

# 未绑定时的状态信息
STATUS_NOT_BOUND = f"您尚未绑定任何账号\n使用 {config.FULL_CMD_BIND} <用户名> 开始绑定"


# ==================== 登录授权相关 ====================

# 未绑定账号时尝试登录的提示
LOGIN_NOT_BOUND = f"❌ 您尚未绑定账号，无法进行登录授权\n请先使用 {config.FULL_CMD_BIND} <用户名> 绑定您的账号"

# 验证码无效或过期
LOGIN_CODE_INVALID = "❌ 验证码无效或已过期\n请重新获取验证码"

# 授权失败
LOGIN_AUTH_FAILED = "❌ 授权失败，请重试"

# 授权成功
LOGIN_AUTH_SUCCESS = """✅ 登录授权成功！
已授权账号: {username}
请返回应用完成登录"""


# ==================== 通知消息 ====================

# 绑定成功通知
NOTIFY_BIND_SUCCESS = "🎉 绑定成功！\n您的 QQ 已成功绑定到账号: {username}"

# 绑定失败通知 - 用户名不匹配
NOTIFY_BIND_USERNAME_MISMATCH = "绑定失败: 用户名不匹配\n期望绑定: {expected}\n实际登录: {actual}"
