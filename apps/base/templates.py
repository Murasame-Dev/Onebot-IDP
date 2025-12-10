"""
HTML 模板
"""

# 成功页面 HTML
SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>绑定成功</title>
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
            max-width: 400px;
        }}
        .success-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #27ae60;
            margin-bottom: 16px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
        .username {{
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>绑定成功!</h1>
        <p>您已成功将 QQ 账号绑定到用户 <span class="username">{username}</span></p>
        <p>您可以关闭此页面了。</p>
    </div>
</body>
</html>
"""

# 失败页面 HTML
ERROR_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>绑定失败</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
        }}
        .error-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #e74c3c;
            margin-bottom: 16px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
        .error-msg {{
            background: #fee;
            padding: 12px;
            border-radius: 8px;
            color: #c0392b;
            margin-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>绑定失败</h1>
        <p class="error-msg">{error}</p>
        <p>请返回 QQ 重新发起绑定请求。</p>
    </div>
</body>
</html>
"""
