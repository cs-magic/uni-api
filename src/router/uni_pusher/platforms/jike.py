from typing import List, Optional

from fastapi import UploadFile, APIRouter, Depends, Form, File, HTTPException
from pydantic import BaseModel, Field

from src.router.uni_pusher.types import PlatformBase, User, PlatfromSession, Twitter


class JikeImage(BaseModel):
    fileUrl: str
    id: str
    key: str


class JikeTopic(BaseModel):
    id: str
    topic: str
    intro: str
    avatar: str


class JikeSession(PlatfromSession):
    """
    necessary fields
    """
    access_token: Optional[str] = Field(None, alias="x-jike-access-token")
    refresh_token: Optional[str] = Field(None, alias="x-jike-refresh-token")
    fetch_ranked_update: Optional[str] = Field(None, alias="fetchRankedUpdate")


async def get_headers(headers: JikeSession = Depends()) -> JikeSession:
    return headers


class JikeSDK(PlatformBase):

    def __init__(self, session: JikeSession):
        self._cookie = session._cookie

    def read_profile(self) -> User:
        import requests

        headers = {**self._cookie,  # 'Host': 'api.ruguoapp.com',
                   'sec-ch-ua-platform': '"macOS"',
                   'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
                   'sec-ch-ua-mobile': '?0',
                   'app-version': '7.27.0',
                   'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                   'accept': 'application/json, text/plain, */*',
                   'dnt': '1',
                   'origin': 'https://web.okjike.com',
                   'sec-fetch-site': 'cross-site',
                   'sec-fetch-mode': 'cors',
                   'sec-fetch-dest': 'empty',
                   'referer': 'https://web.okjike.com/',
                   'accept-language': 'en-US,en;q=0.9',
                   'priority': 'u=1, i', }
        print(f"[headers]: {headers}")

        response = requests.get('https://api.ruguoapp.com/1.0/users/profile', headers=headers)
        return response.json()

    async def push_twitter(self, twitter: Twitter):
        import requests

        cookies = {
            '_ga': 'GA1.2.1329611284.1728629767',
            '_gid': 'GA1.2.1224935922.1730736532',
            '_ga_LQ23DKJDEL': 'GS1.2.1731030933.22.0.1731030933.60.0.0', **self._cookie}

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://web.okjike.com',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', }

        upload_image_token = self.get_upload_image_token()
        image_keys = [(await self.upload_image(upload_image_token, file)).key for file in twitter.images or []]
        json_data = {
            'operationName': 'CreateMessage',
            'variables': {
                'message': {
                    'content': twitter.text,
                    'syncToPersonalUpdate': True,
                    'submitToTopic': twitter.topic,
                    'pictureKeys': image_keys, }, },
            'query': 'mutation CreateMessage($message: CreateMessageInput!) {\n  createMessage(input: $message) {\n    success\n    toast\n    __typename\n  }\n}\n', }

        response = requests.post('https://web-api.okjike.com/api/graphql',
                                 cookies=cookies,
                                 headers=headers,
                                 json=json_data)
        return response.json()

    def search_topics(self, keywords: str) -> List[JikeTopic]:
        import requests

        cookies = {
            '_ga': 'GA1.2.1329611284.1728629767',
            '_gid': 'GA1.2.1224935922.1730736532',
            '_ga_LQ23DKJDEL': 'GS1.2.1730958475.15.1.1730958580.49.0.0', **self._cookie}

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            # 'cookie': '_ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; _ga_LQ23DKJDEL=GS1.2.1730958475.15.1.1730958580.49.0.0; x-apis-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiSmVEU21jcnRIeGhtOVphQW1OYTRcL1ZleWZyTlZ5N1VcL1JCSlRSWENIcFNCXC9Md2g1Ukt1d3NpZUtPSkFqTmhEcDV0K2g5cHVLMGczOE5KdjdXNGFWc0VSTG1PQjMxYWp2N3F1N1F4MlBYSTY5NHJcL0FBVFhMbEJ2eDdHVU1La1VWXC9tdXRtZDdtUklaV1JQdVFYMDNhRkUxZnl5djhtbEhPWFRpMnI5SVlDNHo2eE5NM0ZhYlRYbm9EekhrbmtlbUcxdTdiZ0hvVVFrY0RWa0dTWEMwQVZ4Y2t1ZGZaMTNGRkxlMmNcLzFKNW4xXC9rdUdYQ28xM0FxNnU1dUNiUkJcL0NJa1k5MStMaUpuOGhZV0N2Z2VaeWZKZDVlOW9NNW9lXC84S3dLV0JEMUFlcjJVSVJKUGdDdVNBc2NrcVRkRUNnUjB0bzB0NldYVXR3MkdRYVJyS1ljSngzUGxMQXM2SXZzTUhreGlwMnUydHI0PSIsInYiOjMsIml2IjoiOVNJUkl0S0d5RW16MXhOdzFoamdNUT09IiwiaWF0IjoxNzMwOTY0OTE2LjU3N30.SL2GMJq1TCWRJ9xvyltSG6ueJLzAGYhdY8VWXbhttoI; x-apis-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiSnJYTUY4amE2bzllZEhzQ1d4NHAzc210NW1hc3pYZHdKWTV2M0JSV3haR05FSm5ub1NVQjZqY2tsSjI0eFBSdGdudEdNeHhoRjZMQmYwWTVmaWRXVzFZRHpwYkV0bUN5TUZtbGY5UDZISGJUYlROb1lLTU56QUVOQkdZa1MxOEJcL1dcL0JieEFwMytJNjhrWG9KUzBVd2JVME9XN21RMXBwUE9CRVZ6K3JIV3M9IiwidiI6MywiaXYiOiJORXpuTDlSYkNsdWFEbm1ucERmeVBRPT0iLCJpYXQiOjE3MzA5NjQ5MTYuNTc3fQ.NOIEl6cb77hc1agFClQVjmf3GSyu_NXKQrFHObmBiRQ; fetchRankedUpdate=1730965348254',
            'dnt': '1',
            'origin': 'https://web.okjike.com',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', }

        json_data = {
            'operationName': 'SearchTopics',
            'variables': {'keywords': keywords, },
            'query': 'query SearchTopics($keywords: String!) {\n  search {\n    topics(keywords: $keywords, onlyUserPostEnabled: true) {\n      highlightWord {\n        words\n        singleMaxHighlightTime\n        totalMaxHighlightTime\n        __typename\n      }\n      nodes {\n        id\n        content\n        briefIntro\n        squarePicture {\n          thumbnailUrl\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n', }

        response = requests.post('https://web-api.okjike.com/api/graphql',
                                 cookies=cookies,
                                 headers=headers,
                                 json=json_data)
        data = response.json()
        print("[response] ", data)
        return [JikeTopic(id=node['id'],
                          topic=node['content'],
                          intro=node['briefIntro'],
                          avatar=node['squarePicture']['thumbnailUrl'], ) for node in
                data['data']['search']['topics']['nodes']]

        # Note: json_data will not be serialized by requests  # exactly as it was in the original request.  # data = '{"operationName":"SearchTopics","variables":{"keywords":"吐槽"},"query":"query SearchTopics($keywords: String!) {\\n  search {\\n    topics(keywords: $keywords, onlyUserPostEnabled: true) {\\n      highlightWord {\\n        words\\n        singleMaxHighlightTime\\n        totalMaxHighlightTime\\n        __typename\\n      }\\n      nodes {\\n        id\\n        content\\n        briefIntro\\n        squarePicture {\\n          thumbnailUrl\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'.encode()  # response = requests.post('https://web-api.okjike.com/api/graphql', cookies=cookies, headers=headers, data=data)

    async def upload_image(self, upload_image_token: str, file: UploadFile) -> JikeImage:
        """
        thanks to Cursor:
为什么我上传图片会报错：
uploaded image:  {'error': 'invalid multipart format: multipart: NextPart: bufio: buffer full'}

这个错误通常出现在使用 requests 上传文件时的 multipart 格式问题上。问题出在 upload_image 方法中，当前的实现方式不太合适。让我来修改一下这个方法：
主要修改了以下几点：
移除了不必要的 content-type header，让 requests 自动处理 multipart 格式
简化了 files 和 data 的结构
移除了不必要的 fname 参数
添加了更好的错误处理
        """
        import requests

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'origin': 'https://web.okjike.com',
            'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', }

        try:
            file_content = await file.read()
            files = {'file': (file.filename, file_content, file.content_type or "image/jpeg")}
            data = {'token': upload_image_token}

            response = requests.post('https://upload.qiniup.com/', headers=headers, files=files, data=data)

            data = response.json()
            print("uploaded image: ", data)
            if 'error' in data:
                raise Exception(f"Failed to upload image: {data['error']}")
            return JikeImage(**data)
        finally:
            await file.seek(0)

    def get_upload_image_token(self) -> str:
        import requests

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'origin': 'https://web.okjike.com',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            **self._cookie, }

        response = requests.get('https://upload.ruguoapp.com/1.0/misc/qiniu_uptoken', headers=headers)
        return response.json()['uptoken']


jike_route = APIRouter(prefix='/jike', tags=['即刻'])


@jike_route.get('/profile')
async def read_profile(headers: JikeSession = Depends(get_headers)):
    return JikeSDK(headers).read_profile()


@jike_route.post('/search-topics')
async def search_topics(keywords: str, headers: JikeSession = Depends(get_headers)) -> List[JikeTopic]:
    return JikeSDK(headers).search_topics(keywords)


@jike_route.post('/twitter')
async def push_twitter(
    text: str = Form(None),
    topic: str = Form(None),
    location: str = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    headers: JikeSession = Depends(get_headers)
):
    try:
        twitter: Twitter = Twitter(text=text, topic=topic, images=images, location=location, )
        print("twitter: ", twitter)
        sdk = JikeSDK(headers)
        return await sdk.push_twitter(twitter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
