from typing import Optional

from bs4 import BeautifulSoup
from fastapi import APIRouter
from fastapi.params import Query

from packages.common_common.parse_nested_json import parse_nested_json

wechat_official_account_article_route = APIRouter()


@wechat_official_account_article_route.get('/search-wechat-account')
async def search_wechat_account(keyword: str):
    import requests

    cookies = {
        'nick_name': '%E5%8D%97%E5%B7%9D%20cs-magic.cn',
        'head_img': 'https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FKibtG4nEDDBj37TwUuI3JmzAZiapIAvJoSV4eRVicqG1TYvSzYL0Y1uu5ibBorOoc7OALl8joh4Seib5f9uXx6yXmUqxcCRYcCx1ibdxMNLz9VbxY%2F132',
        'login_type': '2',
        'login_level': '0',
        'sess_skey': '40d4905d20d218e61d0609d5bb6a161d',
        'lbs_refer': '9148bf92cf751e8b928c9e894b2d77c5a8e2dd7def7acc0726f6348c266c73b1cb9b8d4bdee1a2468a6a9937cebb0de5',
        'rewardsn': '',
        'wxtokenkey': '777',
        'ua_id': 'OGpzGrxDKSyFpB0CAAAAACc0teSRXAW6OOVm8fjMDTM=',
        'wxuin': '29306524612717',
        'mm_lang': 'zh_CN',
        'RK': 'oQUlo8vDE8',
        'ptcz': '9934bd7e5323893b885c97efb43a4b899a4c3224ba48ce977ac14c9995865c14',
        'pac_uid': '0_s9titQRhCHN09',
        'suid': 'user_0_s9titQRhCHN09',
        '_qimei_uuid42': '18b03000c06100da01a4e3e21ae9e7ec2712713d2c',
        '_qimei_fingerprint': '7875ed056fef832329aaefeba0b0ed6d',
        '_qimei_h38': '01ed236d01a4e3e21ae9e7ec0300000db18b03',
        '_qimei_q36': '',
        '_clck': '3869894872|1|fqr|0',
        'uuid': 'e18a9373bff122c182348ba8bc497adb',
        'rand_info': 'CAESIFr1nKLQYcoyojO451I8xLLtmODXQatojaW1Bc7PAMr/',
        'slave_bizuin': '3933491917',
        'data_bizuin': '3933491917',
        'bizuin': '3933491917',
        'data_ticket': 'jgqq5S6Mm5uanJcLD8EMWg7rSy2pzZFCTmcYtpmTWW/JywtKGuhziWxHCziCCxTY',
        'slave_sid': 'aFdHc2pGd0pLdWlYQlBjSWhtQXpVNkY1TnhVYTFaVnZRN0JEX2ZUaXlGS29IckdITmVOMkJZTFVtZ1pTYWFBMHo5cmhsMW9yQUE1Z3FBTHJEWk1TN0lSZkozTFZmYXpfaThsOFBPbndzYjBnd3dkVmdZcEpLejBqNnhLQkkxRDFLbEdudWJtY2NVRk5WUEZy',
        'slave_user': 'gh_5babb72c3e78',
        'xid': '5cef913132d5bece960aa647c33e5a57',
        '_clsk': '1l8jrt7|1731255097960|3|1|mp.weixin.qq.com/weheat-agent/payload/record', }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # 'cookie': 'nick_name=%E5%8D%97%E5%B7%9D%20cs-magic.cn; head_img=https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FKibtG4nEDDBj37TwUuI3JmzAZiapIAvJoSV4eRVicqG1TYvSzYL0Y1uu5ibBorOoc7OALl8joh4Seib5f9uXx6yXmUqxcCRYcCx1ibdxMNLz9VbxY%2F132; login_type=2; login_level=0; sess_skey=40d4905d20d218e61d0609d5bb6a161d; lbs_refer=9148bf92cf751e8b928c9e894b2d77c5a8e2dd7def7acc0726f6348c266c73b1cb9b8d4bdee1a2468a6a9937cebb0de5; rewardsn=; wxtokenkey=777; ua_id=OGpzGrxDKSyFpB0CAAAAACc0teSRXAW6OOVm8fjMDTM=; wxuin=29306524612717; mm_lang=zh_CN; RK=oQUlo8vDE8; ptcz=9934bd7e5323893b885c97efb43a4b899a4c3224ba48ce977ac14c9995865c14; pac_uid=0_s9titQRhCHN09; suid=user_0_s9titQRhCHN09; _qimei_uuid42=18b03000c06100da01a4e3e21ae9e7ec2712713d2c; _qimei_fingerprint=7875ed056fef832329aaefeba0b0ed6d; _qimei_h38=01ed236d01a4e3e21ae9e7ec0300000db18b03; _qimei_q36=; _clck=3869894872|1|fqr|0; uuid=e18a9373bff122c182348ba8bc497adb; rand_info=CAESIFr1nKLQYcoyojO451I8xLLtmODXQatojaW1Bc7PAMr/; slave_bizuin=3933491917; data_bizuin=3933491917; bizuin=3933491917; data_ticket=jgqq5S6Mm5uanJcLD8EMWg7rSy2pzZFCTmcYtpmTWW/JywtKGuhziWxHCziCCxTY; slave_sid=aFdHc2pGd0pLdWlYQlBjSWhtQXpVNkY1TnhVYTFaVnZRN0JEX2ZUaXlGS29IckdITmVOMkJZTFVtZ1pTYWFBMHo5cmhsMW9yQUE1Z3FBTHJEWk1TN0lSZkozTFZmYXpfaThsOFBPbndzYjBnd3dkVmdZcEpLejBqNnhLQkkxRDFLbEdudWJtY2NVRk5WUEZy; slave_user=gh_5babb72c3e78; xid=5cef913132d5bece960aa647c33e5a57; _clsk=1l8jrt7|1731255097960|3|1|mp.weixin.qq.com/weheat-agent/payload/record',
        'dnt': '1',
        'priority': 'u=1, i',
        'referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=8&token=1256014245&lang=zh_CN&timestamp=1731253887561',
        'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest', }

    params = {
        'action': 'search_biz',
        'begin': '0',
        'count': '5',
        'query': keyword,
        'token': '1256014245',
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1', }

    response = requests.get('https://mp.weixin.qq.com/cgi-bin/searchbiz',
                            params=params,
                            cookies=cookies,
                            headers=headers)
    return response.json()


async def ensure_wechat_account(keywords: str):
    res = await search_wechat_account(keywords)
    account_list = res['list']
    assert len(account_list) > 0
    account_id = account_list[0]['fakeid']
    assert type(account_id) is str
    return account_id


@wechat_official_account_article_route.get('/article-list')
async def article_list(
    wechat_account_name: Optional[str] = Query(None, description="当指定 name 的时候，id 无效"),
    wechat_account_id: Optional[str] = None,
    begin=0,
    count=5
):
    if wechat_account_name is not None:
        wechat_account_id = await ensure_wechat_account(wechat_account_name)

    assert wechat_account_id is not None, "invalid wechat_account_id"

    import requests

    cookies = {
        'nick_name': '%E5%8D%97%E5%B7%9D%20cs-magic.cn',
        'head_img': 'https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FKibtG4nEDDBj37TwUuI3JmzAZiapIAvJoSV4eRVicqG1TYvSzYL0Y1uu5ibBorOoc7OALl8joh4Seib5f9uXx6yXmUqxcCRYcCx1ibdxMNLz9VbxY%2F132',
        'login_type': '2',
        'login_level': '0',
        'sess_skey': '40d4905d20d218e61d0609d5bb6a161d',
        'lbs_refer': '9148bf92cf751e8b928c9e894b2d77c5a8e2dd7def7acc0726f6348c266c73b1cb9b8d4bdee1a2468a6a9937cebb0de5',
        'rewardsn': '',
        'wxtokenkey': '777',
        'ua_id': 'OGpzGrxDKSyFpB0CAAAAACc0teSRXAW6OOVm8fjMDTM=',
        'wxuin': '29306524612717',
        'mm_lang': 'zh_CN',
        'RK': 'oQUlo8vDE8',
        'ptcz': '9934bd7e5323893b885c97efb43a4b899a4c3224ba48ce977ac14c9995865c14',
        'pac_uid': '0_s9titQRhCHN09',
        'suid': 'user_0_s9titQRhCHN09',
        '_qimei_uuid42': '18b03000c06100da01a4e3e21ae9e7ec2712713d2c',
        '_qimei_fingerprint': '7875ed056fef832329aaefeba0b0ed6d',
        '_qimei_h38': '01ed236d01a4e3e21ae9e7ec0300000db18b03',
        '_qimei_q36': '',
        '_clck': '3869894872|1|fqr|0',
        'uuid': 'e18a9373bff122c182348ba8bc497adb',
        'rand_info': 'CAESIFr1nKLQYcoyojO451I8xLLtmODXQatojaW1Bc7PAMr/',
        'slave_bizuin': '3933491917',
        'data_bizuin': '3933491917',
        'bizuin': '3933491917',
        'data_ticket': 'jgqq5S6Mm5uanJcLD8EMWg7rSy2pzZFCTmcYtpmTWW/JywtKGuhziWxHCziCCxTY',
        'slave_sid': 'aFdHc2pGd0pLdWlYQlBjSWhtQXpVNkY1TnhVYTFaVnZRN0JEX2ZUaXlGS29IckdITmVOMkJZTFVtZ1pTYWFBMHo5cmhsMW9yQUE1Z3FBTHJEWk1TN0lSZkozTFZmYXpfaThsOFBPbndzYjBnd3dkVmdZcEpLejBqNnhLQkkxRDFLbEdudWJtY2NVRk5WUEZy',
        'slave_user': 'gh_5babb72c3e78',
        'xid': '5cef913132d5bece960aa647c33e5a57',
        '_clsk': '1l8jrt7|1731253888023|2|1|mp.weixin.qq.com/weheat-agent/payload/record', }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # 'cookie': 'nick_name=%E5%8D%97%E5%B7%9D%20cs-magic.cn; head_img=https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FKibtG4nEDDBj37TwUuI3JmzAZiapIAvJoSV4eRVicqG1TYvSzYL0Y1uu5ibBorOoc7OALl8joh4Seib5f9uXx6yXmUqxcCRYcCx1ibdxMNLz9VbxY%2F132; login_type=2; login_level=0; sess_skey=40d4905d20d218e61d0609d5bb6a161d; lbs_refer=9148bf92cf751e8b928c9e894b2d77c5a8e2dd7def7acc0726f6348c266c73b1cb9b8d4bdee1a2468a6a9937cebb0de5; rewardsn=; wxtokenkey=777; ua_id=OGpzGrxDKSyFpB0CAAAAACc0teSRXAW6OOVm8fjMDTM=; wxuin=29306524612717; mm_lang=zh_CN; RK=oQUlo8vDE8; ptcz=9934bd7e5323893b885c97efb43a4b899a4c3224ba48ce977ac14c9995865c14; pac_uid=0_s9titQRhCHN09; suid=user_0_s9titQRhCHN09; _qimei_uuid42=18b03000c06100da01a4e3e21ae9e7ec2712713d2c; _qimei_fingerprint=7875ed056fef832329aaefeba0b0ed6d; _qimei_h38=01ed236d01a4e3e21ae9e7ec0300000db18b03; _qimei_q36=; _clck=3869894872|1|fqr|0; uuid=e18a9373bff122c182348ba8bc497adb; rand_info=CAESIFr1nKLQYcoyojO451I8xLLtmODXQatojaW1Bc7PAMr/; slave_bizuin=3933491917; data_bizuin=3933491917; bizuin=3933491917; data_ticket=jgqq5S6Mm5uanJcLD8EMWg7rSy2pzZFCTmcYtpmTWW/JywtKGuhziWxHCziCCxTY; slave_sid=aFdHc2pGd0pLdWlYQlBjSWhtQXpVNkY1TnhVYTFaVnZRN0JEX2ZUaXlGS29IckdITmVOMkJZTFVtZ1pTYWFBMHo5cmhsMW9yQUE1Z3FBTHJEWk1TN0lSZkozTFZmYXpfaThsOFBPbndzYjBnd3dkVmdZcEpLejBqNnhLQkkxRDFLbEdudWJtY2NVRk5WUEZy; slave_user=gh_5babb72c3e78; xid=5cef913132d5bece960aa647c33e5a57; _clsk=1l8jrt7|1731253888023|2|1|mp.weixin.qq.com/weheat-agent/payload/record',
        'dnt': '1',
        'priority': 'u=1, i',
        'referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=8&token=1256014245&lang=zh_CN&timestamp=1731253887561',
        'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest', }

    params = {
        'sub': 'list',
        'search_field': 'null',
        'begin': begin,
        'count': count,
        'query': '',
        'fakeid': wechat_account_id,
        'type': '101_1',
        'free_publish_type': '1',
        'sub_action': 'list_ex',
        'token': '1256014245',
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1', }

    response = requests.get('https://mp.weixin.qq.com/cgi-bin/appmsgpublish',
                            params=params,
                            cookies=cookies,
                            headers=headers)
    data = response.json()
    assert data['base_resp']['ret'] == 0

    # publish_page = json.loads(data['publish_page'])
    return parse_nested_json(data, ['publish_page', 'publish_page.publish_list.publish_info'])


@wechat_official_account_article_route.get('/parse-article')
async def parse_article_route(
    article_id: str, with_article_html=False, with_content_html=True, with_content_md=False, ):
    import requests

    cookies = {
        'nick_name': '%E5%8D%97%E5%B7%9D%20cs-magic.cn',
        'head_img': 'https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FKibtG4nEDDBj37TwUuI3JmzAZiapIAvJoSV4eRVicqG1TYvSzYL0Y1uu5ibBorOoc7OALl8joh4Seib5f9uXx6yXmUqxcCRYcCx1ibdxMNLz9VbxY%2F132',
        'login_type': '2',
        'login_level': '0',
        'sess_skey': '40d4905d20d218e61d0609d5bb6a161d',
        'lbs_refer': '9148bf92cf751e8b928c9e894b2d77c5a8e2dd7def7acc0726f6348c266c73b1cb9b8d4bdee1a2468a6a9937cebb0de5',
        'rewardsn': '',
        'wxtokenkey': '777',
        'ua_id': 'OGpzGrxDKSyFpB0CAAAAACc0teSRXAW6OOVm8fjMDTM=',
        'wxuin': '29306524612717',
        'mm_lang': 'zh_CN',
        'RK': 'oQUlo8vDE8',
        'ptcz': '9934bd7e5323893b885c97efb43a4b899a4c3224ba48ce977ac14c9995865c14',
        'pac_uid': '0_s9titQRhCHN09',
        'suid': 'user_0_s9titQRhCHN09',
        '_qimei_uuid42': '18b03000c06100da01a4e3e21ae9e7ec2712713d2c',
        '_qimei_fingerprint': '7875ed056fef832329aaefeba0b0ed6d',
        '_qimei_h38': '01ed236d01a4e3e21ae9e7ec0300000db18b03',
        '_qimei_q36': '',
        '_clck': '3869894872|1|fqr|0',
        'uuid': 'e18a9373bff122c182348ba8bc497adb',
        'rand_info': 'CAESIFr1nKLQYcoyojO451I8xLLtmODXQatojaW1Bc7PAMr/',
        'slave_bizuin': '3933491917',
        'data_bizuin': '3933491917',
        'bizuin': '3933491917',
        'data_ticket': 'jgqq5S6Mm5uanJcLD8EMWg7rSy2pzZFCTmcYtpmTWW/JywtKGuhziWxHCziCCxTY',
        'slave_sid': 'aFdHc2pGd0pLdWlYQlBjSWhtQXpVNkY1TnhVYTFaVnZRN0JEX2ZUaXlGS29IckdITmVOMkJZTFVtZ1pTYWFBMHo5cmhsMW9yQUE1Z3FBTHJEWk1TN0lSZkozTFZmYXpfaThsOFBPbndzYjBnd3dkVmdZcEpLejBqNnhLQkkxRDFLbEdudWJtY2NVRk5WUEZy',
        'slave_user': 'gh_5babb72c3e78',
        'xid': '5cef913132d5bece960aa647c33e5a57',
        '_clsk': '1l8jrt7|1731255908705|5|1|mp.weixin.qq.com/weheat-agent/payload/record', }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'nick_name=%E5%8D%97%E5%B7%9D%20cs-magic.cn; head_img=https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FKibtG4nEDDBj37TwUuI3JmzAZiapIAvJoSV4eRVicqG1TYvSzYL0Y1uu5ibBorOoc7OALl8joh4Seib5f9uXx6yXmUqxcCRYcCx1ibdxMNLz9VbxY%2F132; login_type=2; login_level=0; sess_skey=40d4905d20d218e61d0609d5bb6a161d; lbs_refer=9148bf92cf751e8b928c9e894b2d77c5a8e2dd7def7acc0726f6348c266c73b1cb9b8d4bdee1a2468a6a9937cebb0de5; rewardsn=; wxtokenkey=777; ua_id=OGpzGrxDKSyFpB0CAAAAACc0teSRXAW6OOVm8fjMDTM=; wxuin=29306524612717; mm_lang=zh_CN; RK=oQUlo8vDE8; ptcz=9934bd7e5323893b885c97efb43a4b899a4c3224ba48ce977ac14c9995865c14; pac_uid=0_s9titQRhCHN09; suid=user_0_s9titQRhCHN09; _qimei_uuid42=18b03000c06100da01a4e3e21ae9e7ec2712713d2c; _qimei_fingerprint=7875ed056fef832329aaefeba0b0ed6d; _qimei_h38=01ed236d01a4e3e21ae9e7ec0300000db18b03; _qimei_q36=; _clck=3869894872|1|fqr|0; uuid=e18a9373bff122c182348ba8bc497adb; rand_info=CAESIFr1nKLQYcoyojO451I8xLLtmODXQatojaW1Bc7PAMr/; slave_bizuin=3933491917; data_bizuin=3933491917; bizuin=3933491917; data_ticket=jgqq5S6Mm5uanJcLD8EMWg7rSy2pzZFCTmcYtpmTWW/JywtKGuhziWxHCziCCxTY; slave_sid=aFdHc2pGd0pLdWlYQlBjSWhtQXpVNkY1TnhVYTFaVnZRN0JEX2ZUaXlGS29IckdITmVOMkJZTFVtZ1pTYWFBMHo5cmhsMW9yQUE1Z3FBTHJEWk1TN0lSZkozTFZmYXpfaThsOFBPbndzYjBnd3dkVmdZcEpLejBqNnhLQkkxRDFLbEdudWJtY2NVRk5WUEZy; slave_user=gh_5babb72c3e78; xid=5cef913132d5bece960aa647c33e5a57; _clsk=1l8jrt7|1731255908705|5|1|mp.weixin.qq.com/weheat-agent/payload/record',
        'dnt': '1',
        'if-modified-since': 'Mon, 11 Nov 2024 00:28:30 +0800',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', }

    article_url = f'https://mp.weixin.qq.com/s/{article_id}'
    response = requests.get(article_url, cookies=cookies, headers=headers)
    article_html = response.text
    soup = BeautifulSoup(article_html, 'html.parser')
    content_html = soup.select_one('#page-content')

    data = {
        "article_url": article_url,
    }
    if with_article_html:
        data['article_html'] = str(article_html)
    if with_content_html:
        data['content_html'] = str(content_html)
    if with_content_md:
        data['content_md'] = str(content_html)

    data['is_paid'] = bool(content_html.select_one('.js_pay_preview_filter'))

    return data
