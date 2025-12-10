"""
OAuth2 IDP 登录页面 HTML 模板
"""

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QQ 登录验证</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 450px;
        }}
        .logo {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 16px;
            font-size: 24px;
        }}
        .code-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 48px;
            font-weight: bold;
            letter-spacing: 12px;
            padding: 24px 32px;
            border-radius: 12px;
            margin: 24px 0;
            font-family: 'Courier New', monospace;
        }}
        .instructions {{
            color: #666;
            line-height: 1.8;
            margin-bottom: 20px;
        }}
        .command {{
            background: #f5f5f5;
            padding: 12px 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 18px;
            color: #333;
            display: inline-block;
        }}
        .expire {{
            color: #999;
            font-size: 14px;
            margin-top: 20px;
        }}
        .waiting {{
            margin-top: 24px;
            padding: 16px;
            background: #e8f4fd;
            border-radius: 8px;
            color: #1976d2;
        }}
        .spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #1976d2;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔐</div>
        <h1>QQ 账号登录验证</h1>
        <p class="instructions">请在 QQ 群聊或私聊中发送以下命令完成登录：</p>
        <div class="command">{login_cmd} {login_code}</div>
        <div class="code-box">{login_code}</div>
        <p class="expire">验证码将在 <span id="countdown">{expire_seconds}</span> 秒后过期</p>
        <div class="waiting" id="waiting-status">
            <span class="spinner"></span>
            等待验证中...
        </div>
        <div class="expired-msg" id="expired-status" style="display:none; margin-top:24px; padding:16px; background:#fee; border-radius:8px; color:#c0392b;">
            ❌ 验证码已过期，请刷新页面重新获取
        </div>
    </div>
    <script>
        const loginCode = "{login_code}";
        const expireSeconds = {expire_seconds};
        let remainingSeconds = expireSeconds;
        let isExpired = false;
        
        // 倒计时显示
        const countdownEl = document.getElementById('countdown');
        const countdownInterval = setInterval(() => {{
            remainingSeconds--;
            if (remainingSeconds <= 0) {{
                clearInterval(countdownInterval);
                countdownEl.textContent = '0';
                showExpired();
            }} else {{
                countdownEl.textContent = remainingSeconds;
            }}
        }}, 1000);
        
        function showExpired() {{
            isExpired = true;
            document.getElementById('waiting-status').style.display = 'none';
            document.getElementById('expired-status').style.display = 'block';
            document.querySelector('.code-box').style.opacity = '0.5';
            document.querySelector('.command').style.opacity = '0.5';
        }}
        
        // 每2秒检查授权状态
        const checkInterval = setInterval(async () => {{
            if (isExpired) {{
                clearInterval(checkInterval);
                return;
            }}
            try {{
                const response = await fetch(`/oauth/check_status?login_code=${{loginCode}}`);
                const data = await response.json();
                if (data.authorized) {{
                    clearInterval(checkInterval);
                    clearInterval(countdownInterval);
                    window.location.href = data.redirect_url;
                }} else if (data.status === 'expired') {{
                    clearInterval(checkInterval);
                    clearInterval(countdownInterval);
                    showExpired();
                }}
            }} catch (e) {{
                console.error('检查状态失败:', e);
            }}
        }}, 2000);
    </script>
</body>
</html>
"""
