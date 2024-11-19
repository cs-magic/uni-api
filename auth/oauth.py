from fastapi import HTTPException
import httpx
from typing import Optional
from settings import settings
from schema.user import UserCreate


class OAuthHandler:
    async def verify_oauth_token(self, token: str, provider: str) -> Optional[UserCreate]:
        if provider == "google":
            return await self._verify_google_token(token)
        elif provider == "github":
            return await self._verify_github_token(token)
        elif provider == "wechat":
            return await self._verify_wechat_token(token)
        else:
            raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

    async def _verify_google_token(self, token: str) -> Optional[UserCreate]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Google token")
            
            data = response.json()
            return UserCreate(
                username=data["email"].split("@")[0],
                email=data["email"],
                full_name=data.get("name"),
                oauth_provider="google",
                oauth_id=data["sub"]
            )

    async def _verify_github_token(self, token: str) -> Optional[UserCreate]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"token {token}"}
            response = await client.get(
                "https://api.github.com/user",
                headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid GitHub token")
            
            data = response.json()
            return UserCreate(
                username=data["login"],
                email=data.get("email"),
                full_name=data.get("name"),
                oauth_provider="github",
                oauth_id=str(data["id"])
            )

    async def _verify_wechat_token(self, token: str) -> Optional[UserCreate]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.weixin.qq.com/sns/userinfo",
                params={
                    "access_token": token,
                    "openid": settings.WECHAT_APP_ID
                }
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid WeChat token")
            
            data = response.json()
            return UserCreate(
                username=f"wx_{data['openid']}",
                full_name=data.get("nickname"),
                oauth_provider="wechat",
                oauth_id=data["openid"]
            ) 