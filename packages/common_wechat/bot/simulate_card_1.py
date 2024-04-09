from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from packages.common_datetime.utils import get_current_timestamp
from packages.common_common.parse_first_url import parse_first_url
from settings import settings


def simulate_card_1(target_url: str, user_name: str = None, user_avatar: str = None):
    try:
        logger.debug("-- starting browser")
        # todo: conditional
        service = Service(ChromeDriverManager().install())
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.debug("-- visiting")
        driver.get(f'{settings.FRONTEND_BASEURL}/card/gen')
        
        if user_name:
            logger.debug("-- filling user name")
            driver.find_element(By.ID, "card-user-name").send_keys(user_name)
        
        if user_avatar:
            logger.debug("-- filling user avatar")
            driver.find_element(By.ID, "card-user-avatar").send_keys(user_avatar)
        
        logger.debug("-- filling url")
        driver.find_element(By.ID, "card-input-url").send_keys(target_url)
        
        logger.debug("-- clicking generate button")
        driver.find_element(By.ID, "generate-card").click()
        
        logger.debug("-- waiting upload button")
        #   生成图片需要爬取页面与调用大模型，会慢很多
        WebDriverWait(driver, 60).until(
            expected_conditions.element_to_be_clickable((By.ID, "upload-card"))
        ).click()
        
        logger.debug("-- waiting uploaded result")
        # 上传图片则比较简单
        uploaded_tip = WebDriverWait(driver, 10).until(
            expected_conditions.visibility_of_element_located((
                By.CSS_SELECTOR, ".toaster div[data-title]"))
        ).text
        
        oss_url = parse_first_url(uploaded_tip)
        logger.info(f"-- oss url: {oss_url}")
        return {"url": oss_url, "name": f"{get_current_timestamp(kind='s')}.png"}
    
    except Exception as e:
        logger.error(e)
        return None
