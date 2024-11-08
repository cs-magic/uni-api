from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/jike/search")
async def jike_search(
    keywords : str,
    limit_quanzi: bool = False,
    custom_cookie: Optional[str] = Header(""),
    sec_ch_ua_platform: Optional[str] = Header(""),
    user_agent: Optional[str] = Header("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
    accept: Optional[str] = Header("*/*"),
    sec_ch_ua: Optional[str] = Header(""),
    content_type: Optional[str] = Header("application/json"),
    dnt: Optional[str] = Header("1"),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    origin: Optional[str] = Header("https://web.okjike.com"),
    sec_fetch_site: Optional[str] = Header("same-site"),
    sec_fetch_mode: Optional[str] = Header("cors"),
    sec_fetch_dest: Optional[str] = Header("empty"),
    accept_language: Optional[str] = Header("en-US,en;q=0.9"),
    priority: Optional[str] = Header("u=1, i")
):
    """
    Route generated from curl command
    Original URL: https://web-api.okjike.com/api/graphql
    Method: POST
    """

    request_data: Dict[str, Any] = {'operationName': 'SearchIntegrate', 'variables': {'keywords': keywords}, 'query': 'query SearchIntegrate($keywords: String!, $loadMoreKey: JSON) { search { integrate(keywords: $keywords, loadMoreKey: $loadMoreKey) { pageInfo { hasNextPage loadMoreKey __typename } highlightWord { words singleMaxHighlightTime totalMaxHighlightTime __typename } nodes { ... on SearchIntegrateSection { sectionType: type sectionViewType sectionContent: content title __typename } ... on SearchIntegrateUserSection { items { ...TinyUserFragment following __typename } __typename } ... on TopicInfo { ...TopicItemFragment __typename } ... on OriginalPost { ...FeedMessageFragment __typename } __typename } __typename } __typename } } fragment TinyUserFragment on UserInfo { avatarImage { thumbnailUrl smallPicUrl picUrl __typename } isSponsor username screenName briefIntro __typename } fragment TopicItemFragment on TopicInfo { id messagePrefix content intro subscribedStatusRawValue subscribersCount squarePicture { smallPicUrl middlePicUrl picUrl __typename } tips { inComment inDraft __typename } subscribersTextSuffix subscribersName recentPost __typename } fragment FeedMessageFragment on MessageEssential { ...EssentialFragment ... on OriginalPost { ...LikeableFragment ...CommentableFragment ...RootMessageFragment ...UserPostFragment ...MessageInfoFragment isPrivate pinned { personalUpdate __typename } __typename } ... on Repost { ...LikeableFragment ...CommentableFragment ...UserPostFragment ...RepostFragment isPrivate pinned { personalUpdate __typename } __typename } ... on Question { ...UserPostFragment __typename } ... on OfficialMessage { ...LikeableFragment ...CommentableFragment ...MessageInfoFragment ...RootMessageFragment __typename } __typename } fragment EssentialFragment on MessageEssential { id type content shareCount repostCount createdAt collected pictures { format watermarkPicUrl picUrl thumbnailUrl smallPicUrl width height __typename } urlsInText { url originalUrl title __typename } __typename } fragment LikeableFragment on LikeableMessage { liked likeCount __typename } fragment CommentableFragment on CommentableMessage { commentCount __typename } fragment RootMessageFragment on RootMessage { topic { id content __typename } __typename } fragment UserPostFragment on MessageUserPost { readTrackInfo user { ...TinyUserFragment __typename } __typename } fragment MessageInfoFragment on MessageInfo { video { title type image { picUrl __typename } __typename } linkInfo { originalLinkUrl linkUrl title pictureUrl linkIcon audio { title type image { thumbnailUrl picUrl __typename } author __typename } video { title type image { picUrl __typename } __typename } __typename } __typename } fragment RepostFragment on Repost { target { ...RepostTargetFragment __typename } targetType __typename } fragment RepostTargetFragment on RepostTarget { ... on OriginalPost { id type content pictures { thumbnailUrl __typename } topic { id content __typename } user { ...TinyUserFragment __typename } __typename } ... on Repost { id type content pictures { thumbnailUrl __typename } user { ...TinyUserFragment __typename } __typename } ... on Question { id type content pictures { thumbnailUrl __typename } user { ...TinyUserFragment __typename } __typename } ... on Answer { id type content pictures { thumbnailUrl __typename } user { ...TinyUserFragment __typename } __typename } ... on OfficialMessage { id type content pictures { thumbnailUrl __typename } __typename } ... on DeletedRepostTarget { status __typename } __typename } '},

    # Construct headers
    headers = {
        "Cookie": custom_cookie,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "user-agent": user_agent,
        "accept": accept,
        "sec-ch-ua": sec_ch_ua,
        "content-type": content_type,
        "dnt": dnt,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "origin": origin,
        "sec-fetch-site": sec_fetch_site,
        "sec-fetch-mode": sec_fetch_mode,
        "sec-fetch-dest": sec_fetch_dest,
        "accept-language": accept_language,
        "priority": priority,
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
        # Send POST request
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=request_data,
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

