from bs4 import BeautifulSoup
from fastapi import APIRouter

from src.router.wechat.official_account.article import parse_article_route

lijigang_route = APIRouter(prefix='/lijigang')


def extract_lijigang_code(html_content):
    """
    Extract code content containing '李继刚' and replace <br> with \n.

    Args:
        html_content (str): Input HTML string containing code

    Returns:
        str: Processed code content
    """
    # Check if the content contains the required name
    if "李继刚" not in html_content:
        return ""

    # Extract content between <code> tags
    start_idx = html_content.find("<code")
    end_idx = html_content.find("</code>")

    if start_idx == -1 or end_idx == -1:
        return ""

    # Find the actual content start after the first >
    content_start = html_content.find(">", start_idx) + 1
    code_content = html_content[content_start:end_idx]

    # Replace <br> with \n
    code_content = code_content.replace("<br/>", "\n")

    return code_content


@lijigang_route.get('/parse')
async def parse_lijigang_article(
    article_id: str = 'EV2gRTeD_6NtDaaANTT7TQ'
):
    data = await parse_article_route(article_id, with_content_html=True)

    content_str = data['content_html']
    content_html = BeautifulSoup(content_str, 'html.parser')

    # prmpt_html = content_html.select_one('#page-content')
    prompt_str = extract_lijigang_code(content_str)

    images = content_html.select('img')
    def parse_image(image):
        return {
            # "width": image.get("data-w"),
            "ratio": image.get("data-ratio"),
            "src": image.get("data-src"),
        }
    del data['content_html']
    data['prompt'] = prompt_str
    data["images"] = [parse_image(image) for image in images]
    return data