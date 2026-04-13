"""微信 API 封装 — code2session"""

import httpx
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger("wechat")
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

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(CODE2SESSION_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.TimeoutException:
            logger.error("微信 code2session 请求超时")
            raise ValueError("微信登录服务超时，请稍后重试")
        except httpx.HTTPStatusError as e:
            logger.error(f"微信 code2session HTTP错误: {e}")
            raise ValueError("微信登录服务异常")

    if "errcode" in data and data["errcode"] != 0:
        logger.warning(f"微信 code2session 返回错误: {data}")
        raise ValueError(f"微信登录失败: {data.get('errmsg', 'unknown error')}")

    return {
        "openid": data["openid"],
        "session_key": data.get("session_key", ""),
        "unionid": data.get("unionid"),
    }
