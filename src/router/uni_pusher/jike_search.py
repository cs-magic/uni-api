from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/jike/search")
async def jike_search(
    request_data: Dict[str, Any] = {'operationName': 'SearchIntegrate', 'variables': {'keywords': '创业者'}, 'query': 'query SearchIntegrate($keywords: String!, $loadMoreKey: JSON) { search { integrate(keywords: $keywords, loadMoreKey: $loadMoreKey) { pageInfo { hasNextPage loadMoreKey __typename } highlightWord { words singleMaxHighlightTime totalMaxHighlightTime __typename } nodes { ... on SearchIntegrateSection { sectionType: type sectionViewType sectionContent: content title __typename } ... on SearchIntegrateUserSection { items { ...TinyUserFragment following __typename } __typename } ... on TopicInfo { ...TopicItemFragment __typename } ... on OriginalPost { ...FeedMessageFragment __typename } __typename } __typename } __typename } } fragment TinyUserFragment on UserInfo { avatarImage { thumbnailUrl smallPicUrl picUrl __typename } isSponsor username screenName briefIntro __typename } fragment TopicItemFragment on TopicInfo { id messagePrefix content intro subscribedStatusRawValue subscribersCount squarePicture { smallPicUrl middlePicUrl picUrl __typename } tips { inComment inDraft __typename } subscribersTextSuffix subscribersName recentPost __typename } fragment FeedMessageFragment on MessageEssential { ...EssentialFragment ... on OriginalPost { ...LikeableFragment ...CommentableFragment ...RootMessageFragment ...UserPostFragment ...MessageInfoFragment isPrivate pinned { personalUpdate __typename } __typename } ... on Repost { ...LikeableFragment ...CommentableFragment ...UserPostFragment ...RepostFragment isPrivate pinned { personalUpdate __typename } __typename } ... on Question { ...UserPostFragment __typename } ... on OfficialMessage { ...LikeableFragment ...CommentableFragment ...MessageInfoFragment ...RootMessageFragment __typename } __typename } fragment EssentialFragment on MessageEssential { id type content shareCount repostCount createdAt collected pictures { format watermarkPicUrl picUrl thumbnailUrl smallPicUrl width height __typename } urlsInText { url originalUrl title __typename } __typename } fragment LikeableFragment on LikeableMessage { liked likeCount __typename } fragment CommentableFragment on CommentableMessage { commentCount __typename } fragment RootMessageFragment on RootMessage { topic { id content __typename } __typename } fragment UserPostFragment on MessageUserPost { readTrackInfo user { ...TinyUserFragment __typename } __typename } fragment MessageInfoFragment on MessageInfo { video { title type image { picUrl __typename } __typename } linkInfo { originalLinkUrl linkUrl title pictureUrl linkIcon audio { title type image { thumbnailUrl picUrl __typename } author __typename } video { title type image { picUrl __typename } __typename } __typename } __typename } fragment RepostFragment on Repost { target { ...RepostTargetFragment __typename } targetType __typename } fragment RepostTargetFragment on RepostTarget { ... on OriginalPost { id type content pictures { thumbnailUrl __typename } topic { id content __typename } user { ...TinyUserFragment __typename } __typename } ... on Repost { id type content pictures { thumbnailUrl __typename } user { ...TinyUserFragment __typename } __typename } ... on Question { id type content pictures { thumbnailUrl __typename } user { ...TinyUserFragment __typename } __typename } ... on Answer { id type content pictures { thumbnailUrl __typename } user { ...TinyUserFragment __typename } __typename } ... on OfficialMessage { id type content pictures { thumbnailUrl __typename } __typename } ... on DeletedRepostTarget { status __typename } __typename } '},
    custom_cookie: Optional[str] = Header("_ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; fetchRankedUpdate=1730903010810; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiaVMycjV1Qm5BWFlHUkRoV3JuNzNFejZEaDdISjgrWHRQNGJHUEdwUG1GRmsrdUJ1b0hCWnpqelhqRXg2bjluRWJHaHhER0RHR1dNT3lGbXo0VFdCaFM0R1cxbDc5REc1MmNGbWRKWkhYN2xTOTdxWDIrMXZZUXh0dEZkUUxScWZiZHBuS0RSSlZFZFd3XC83dTdsa3kwekZ1NkxJQldVQlwvVzBEdlBkcjNFZDIrbzM2Vjk5Q0t3SGowbkJVaVlwXC8zcmlhb2Q3aHBXUytTaUxHZmNIcU1USjRSZGJcL3dTNGk3XC9VTjMrbkYzb0FjcnpvbHYxQVdkZEF6cnV5VmRYbGhpRFJiK3FCUDl4RFRwNE53MkMrcE5FWkU5RFlDZ3ZUZVBaNGRKRUlJYzFPZUF6UjNTdGpiSVhTV0VkblQwTThCQXJhTUUxN01nU0N0bmlxY2pBbkVDTGZ6VjNuU0N0WG9RT3FENmxYK3ZTemM9IiwidiI6MywiaXYiOiJHamU4S0pLZnhNTkVWd3g3dU9wV2V3PT0iLCJpYXQiOjE3MzA5MTA4NzAuMDJ9.u-Cz75T_zvLQE9cOF7O1YADbctoABvOd8GdFskG4HsA; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiaTNDSTJTMGF2S1wvVGszZkN5TWtLUXBtT2RRRGhGQzJKc2NqS0swUlUwV0dqYmVZbUZDODluYk9ZcXZydnFJWHpiMFVBVVBvbnRGZUl5MUNSdXFCMk92b29RQlI0dUZiVm9lY1dEdXZJOUhUR2RNZkV5S0RnU0ZQSlBXZmlNdXgyY2JyVENXR0VHd3k1a0p4UlArUTBWcUZCNmdLa0xYalVEMEVzeGlqZEF5MD0iLCJ2IjozLCJpdiI6InBlRnUxemU2RzZ4OCtieEZXMkY3ZVE9PSIsImlhdCI6MTczMDkxMDg3MC4wMn0.vphQL0uYVwhSPzom9NnCOiQyigXDsT7FRia1oxgGiQQ; _gat=1; _ga_LQ23DKJDEL=GS1.2.1730908772.14.1.1730911595.60.0.0"),
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
) -> Dict[str, Any]:
    """
    Route generated from curl command
    Original URL: https://web-api.okjike.com/api/graphql
    Method: POST
    """
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

