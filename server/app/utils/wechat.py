"""微信 API 封装 — code2session"""

import httpx
from app.config import get_settings

settings = get_settings()

CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def code2session(code: str) -> dict:
    """调用微信 code2session 接口，获取 openid 和 session_key"""
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(CODE2SESSION_URL, params=params)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise ValueError(f"微信登录失败: {data.get('errmsg', 'unknown error')}")

    return {
        "openid": data["openid"],
        "session_key": data.get("session_key", ""),
        "unionid": data.get("unionid"),
    }
