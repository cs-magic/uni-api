from fastapi import APIRouter, Header, File, UploadFile, Form
from typing import Optional, Dict, Any
import requests
import json

jike_upload_image_route = APIRouter()

BASE_URL = "https://upload.qiniup.com/"
method = "POST"

@jike_upload_image_route.post("/jike/upload-image")
async def jike_upload_image(
    file: UploadFile = File(...),
    token: str = Form(...),
    fname: str = Form(...),
    accept: Optional[str] = Header("*/*"),
    accept_language: Optional[str] = Header("en-US,en;q=0.9"),
    content_type: Optional[str] = Header("multipart/form-data; boundary=----WebKitFormBoundarycvrUxfzOXJe7uWSq"),
    dnt: Optional[str] = Header("1"),
    origin: Optional[str] = Header("https://web.okjike.com"),
    priority: Optional[str] = Header("u=1, i"),
    sec_ch_ua: Optional[str] = Header(""),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    sec_ch_ua_platform: Optional[str] = Header(""),
    sec_fetch_dest: Optional[str] = Header("empty"),
    sec_fetch_mode: Optional[str] = Header("cors"),
    sec_fetch_site: Optional[str] = Header("cross-site"),
    user_agent: Optional[str] = Header("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
):
    """
    Route generated from curl command
    Original URL: https://upload.qiniup.com/
    Method: POST
    """
    # Construct headers
    headers = {
        "accept": accept,
        "accept-language": accept_language,
        "dnt": dnt,
        "origin": origin,
        "priority": priority,
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "sec-fetch-dest": sec_fetch_dest,
        "sec-fetch-mode": sec_fetch_mode,
        "sec-fetch-site": sec_fetch_site,
        "user-agent": user_agent,
    }
    
    # Remove None values from headers
    headers = {k: v for k, v in headers.items() if v is not None}
    
    try:
        # Add common headers
        headers.update({
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        })

        # Prepare multipart form data
        files = {}
        data = {}
        # Handle file upload for file
        files["file"] = (
            file.filename,
            await file.read(),
            file.content_type or "image/jpeg"
        )
        # Handle form field token
        data["token"] = token
        # Handle form field fname
        data["fname"] = fname
        
        # Send multipart request
        response = requests.request(
            method,
            BASE_URL,
            headers=headers,
            files=files,
            data=data,
            verify=True
        )

        # Check response status
        response.raise_for_status()
        
        # Try to parse JSON response
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"response": response.text}
            
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None),
            "response_text": getattr(e.response, "text", None)
        } 