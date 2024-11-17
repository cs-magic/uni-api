import uncurl

print(uncurl.parse('''curl 'https://web-api.okjike.com/api/graphql' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'content-type: application/json' \
  -H 'cookie: _ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; fetchRankedUpdate=1731009410093; _ga_LQ23DKJDEL=GS1.2.1731028318.21.1.1731028352.26.0.0; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiUk40ZkQ0VWhMUkJLaVlPbVlRZTV2a3BtRFNCZTd5SlhFeUtMVVBvNlJ4UlpkVDJJRGRBS1YxY2ZITUVWUXBwXC9Uc2srTmlIR2h4TG1kS1wvVE9lQkcwN2VsV1pNMStHcm9TYXh2aENZcE1Od1FFVHNrSWJ0UVdUNTF1Y2dtRXY2NXVmeEdSMTBqa1BhZ2lrd0RVUkJvb2Jud3BCOUZZSCtsc0Q0YVNucTgrVG94RHNGeENjOGxsc0FxbGFQOGh3c0lVbWhXVVZJaFpSUDhuRDg3TmVjR05iZ0Q3UEJFUld6MlJBWFBFNWxtVEp0c0hCakErQXdkaG9zNFwvekxDVW43NjFkQjBGZldwSmxxcUxQSGhlUk85R3V1MnZ3aVdXdUI0NXdcL3hlZ01vNGFSMG9WTzV6em40K2FrQndsb1VpWEpSK0d5RjJcL25KemVDbFFvaHlWMEIxVHZHRlhUYm9vYlVoVFh2UkJNVGFuNEE9IiwidiI6MywiaXYiOiJTa3hSNzN3aWM0dTV3dkVJaG9VK3dBPT0iLCJpYXQiOjE3MzEwMjg1OTQuMzMzfQ.IWOWTESXCdi3ypGRee-NWJXMoaW1WnrKyKYKApCUXbY; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoidlc2V1BDRmRrZTU3Sm9IR3BtSW5WTm5sMFg1RndjUUQ2SHEreWhRZlZjUUd0amQzUU5FR0Jka3VueXpZbVwveDUwRkQwYmZxcnNmS3NUWml0UStcLytMaXVOaDU5SnBRZDM4VFdcLzNUcWh3dTdCdVFQQXFDVVQyUG05QWFBamZicVZ1djZXNHhVV2p1dmNmcU5rNmo5V21DZHhuVGVQZW03eWtTaFBVYUV5dXNzPSIsInYiOjMsIml2IjoibGFyOFJmc1g0dU9PZXBhS2V6VjFcL3c9PSIsImlhdCI6MTczMTAyODU5NC4zMzN9.LvK_9v8ZiX7LRVbYIuyRPywupvNnc6u6E3lB-KOIw34; _gat=1' \
  -H 'dnt: 1' \
  -H 'origin: https://web.okjike.com' \
  -H 'priority: u=1, i' \
  -H 'sec-ch-ua: "Not?A_Brand";v="99", "Chromium";v="130"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' \
  --data-raw $'{"operationName":"SubscribedTopic","variables":{"username":"2df8ed5f-d1e4-43c2-9809-ad32058159d3"},"query":"query SubscribedTopic($username: String\u0021, $loadMoreKey: JSON) {\\n  viewer {\\n    listToppingTopics {\\n      count\\n      limit\\n      shortcuts {\\n        ...TopicItemFragment\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  userProfile(username: $username) {\\n    listSubscribedTopics(input: {filterShortcuts: \\"true\\", includeRecentPost: \\"true\\"}, loadMoreKey: $loadMoreKey) {\\n      pageInfo {\\n        loadMoreKey\\n        hasNextPage\\n        __typename\\n      }\\n      nodes {\\n        ...TopicItemFragment\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment TopicItemFragment on TopicInfo {\\n  id\\n  messagePrefix\\n  content\\n  intro\\n  subscribedStatusRawValue\\n  subscribersCount\\n  squarePicture {\\n    smallPicUrl\\n    middlePicUrl\\n    picUrl\\n    __typename\\n  }\\n  tips {\\n    inComment\\n    inDraft\\n    __typename\\n  }\\n  subscribersTextSuffix\\n  subscribersName\\n  recentPost\\n  __typename\\n}\\n"}' '''))