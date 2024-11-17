from typing import List, Optional

from pydantic import BaseModel, Field

from packages.common import DEFAULT_AREA_CODE
from packages.common.upload_file import UploadFileInfo
from router.uni_pusher.types import PlatformSession, PlatformBase, User, Topic, Twitter


class JikeImage(BaseModel):
    fileUrl: str
    id: str
    key: str


class JikeSession(PlatformSession):
    """
    necessary fields
    """
    access_token: Optional[str] = Field(None, alias="x-jike-access-token")
    refresh_token: Optional[str] = Field(None, alias="x-jike-refresh-token")
    fetch_ranked_update: Optional[str] = Field(None, alias="fetchRankedUpdate")


class JikeAuth(BaseModel):

    def get_verification_code(self, phone_number: str, area_code=DEFAULT_AREA_CODE) -> str:
        import requests

        cookies = {
            '_gid': 'GA1.2.499475221.1731253561',
            '_ga': 'GA1.2.1329611284.1728629767',
            '_ga_5ES45LSTYC': 'GS1.1.1731328711.2.1.1731328726.45.0.0',
            'fetchRankedUpdate': get_fetchRankedUpdate(),
            '_gat': '1',
            '_ga_LQ23DKJDEL': 'GS1.2.1731334435.26.1.1731336502.58.0.0', }

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

        json_data = {
            'operationName': 'GetSmsCode',
            'variables': {'mobilePhoneNumber': phone_number, 'areaCode': area_code, },
            'query': 'mutation GetSmsCode($mobilePhoneNumber: String!, $areaCode: String!) {\n  getSmsCode(action: PHONE_MIX_LOGIN, mobilePhoneNumber: $mobilePhoneNumber, areaCode: $areaCode) {\n    action\n    __typename\n  }\n}\n', }

        response = requests.post('https://web-api.okjike.com/api/graphql',
                                 cookies=cookies,
                                 headers=headers,
                                 json=json_data)

        return response.json()

    def verify_code(self, phone_number: str, area_code =DEFAULT_AREA_CODE, *, code: str) -> JikeSession:
        import requests

        cookies = {
            '_gid': 'GA1.2.499475221.1731253561',
            '_ga': 'GA1.2.1329611284.1728629767',
            '_ga_5ES45LSTYC': 'GS1.1.1731328711.2.1.1731328726.45.0.0',
            'fetchRankedUpdate': get_fetchRankedUpdate(),
            '_ga_LQ23DKJDEL': 'GS1.2.1731334435.26.1.1731336502.58.0.0', }

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

        json_data = {
            'operationName': 'MixLoginWithPhone',
            'variables': {'smsCode': code, 'mobilePhoneNumber': phone_number, 'areaCode': area_code, },
            'query': 'mutation MixLoginWithPhone($smsCode: String!, $mobilePhoneNumber: String!, $areaCode: String!) {\n  mixLoginWithPhone(smsCode: $smsCode, mobilePhoneNumber: $mobilePhoneNumber, areaCode: $areaCode) {\n    isRegister\n    user {\n      distinctId: id\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TinyUserFragment on UserInfo {\n  avatarImage {\n    thumbnailUrl\n    smallPicUrl\n    picUrl\n    __typename\n  }\n  isSponsor\n  username\n  screenName\n  briefIntro\n  __typename\n}\n', }

        response = requests.post('https://web-api.okjike.com/api/graphql',
                                 cookies=cookies,
                                 headers=headers,
                                 json=json_data)
        print("response headers: ", response.headers)
        return {"result": response.json(), "headers": response.headers.get("set-cookie")}

    def refresh_token(self, refresh_token: str):
        import requests

        cookies = {
            '_gid': 'GA1.2.499475221.1731253561',
            '_ga': 'GA1.2.1329611284.1728629767',
            '_ga_5ES45LSTYC': 'GS1.1.1731328711.2.1.1731328726.45.0.0',
            'fetchRankedUpdate': get_fetchRankedUpdate(),
            'x-jike-refresh-token': refresh_token,
            '_ga_LQ23DKJDEL': 'GS1.2.1731334435.26.1.1731337496.60.0.0', }

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

        json_data = {
            'operationName': 'refreshToken',
            'variables': {},
            'query': 'mutation refreshToken {\n  refreshToken {\n    accessToken\n    refreshToken\n  }\n}\n', }

        response = requests.post('https://web-api.okjike.com/api/graphql',
                                 cookies=cookies,
                                 headers=headers,
                                 json=json_data)

        # Note: json_data will not be serialized by requests
        # exactly as it was in the original request.
        # data = '{"operationName":"refreshToken","variables":{},"query":"mutation refreshToken {\\n  refreshToken {\\n    accessToken\\n    refreshToken\\n  }\\n}\\n"}'
        # response = requests.post('https://web-api.okjike.com/api/graphql', cookies=cookies, headers=headers, data=data)
        return response.json()


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

    def post_twitter(self, twitter: Twitter):
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
        image_keys = []
        for file in (twitter.images or []):
            if isinstance(file, UploadFileInfo):
                image = self.upload_image(upload_image_token, file)
            else:
                raise ValueError("Unsupported file type")
            image_keys.append(image.key)
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

    def search_topics(self, keywords: str) -> List[Topic]:
        import requests

        cookies = {
            '_ga': 'GA1.2.1329611284.1728629767',
            '_gid': 'GA1.2.1224935922.1730736532',
            '_ga_LQ23DKJDEL': 'GS1.2.1730958475.15.1.1730958580.49.0.0', **self._cookie}

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
        return [Topic(id=node['id'],
                      topic=node['content'],
                      intro=node['briefIntro'],
                      avatar=node['squarePicture']['thumbnailUrl'], ) for node in
                data['data']['search']['topics']['nodes']]

    def upload_image(self, upload_image_token: str, file: UploadFileInfo) -> JikeImage:
        """
        Upload image to Jike platform
        
        Args:
            upload_image_token: Token for upload authorization
            file: File information containing filename, content and content type
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
            files = {'file': (file.filename, file.content, file.content_type)}
            data = {'token': upload_image_token}

            response = requests.post('https://upload.qiniup.com/', headers=headers, files=files, data=data)

            data = response.json()
            print("uploaded image: ", data)
            if 'error' in data:
                raise Exception(f"Failed to upload image: {data['error']}")
            return JikeImage(**data)
        except Exception as e:
            raise Exception(f"Failed to upload image: {str(e)}")

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

    def check_rss(self):
        import requests

        cookies = {
            '_gid': 'GA1.2.499475221.1731253561',
            '_ga': 'GA1.2.1329611284.1728629767',
            '_ga_5ES45LSTYC': 'GS1.1.1731328711.2.1.1731328726.45.0.0', **self._cookie, }

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

        json_data = {
            'operationName': 'UnreadNotification',
            'variables': {},
            'query': 'query UnreadNotification {\n  viewer {\n    unread {\n      systemNotification {\n        unreadCount\n        __typename\n      }\n      notification {\n        unreadCount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n', }

        response = requests.post('https://web-api.okjike.com/api/graphql',
                                 cookies=cookies,
                                 headers=headers,
                                 json=json_data)
        return response.json()


def get_fetchRankedUpdate():
    """
    todo: how to update ?
    """
    # return str(time.time() * 1e3)
    return '1731329783673'
