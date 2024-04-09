import json
import re
import shutil
import time
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image
from loguru import logger
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from packages.common_datetime.utils import get_current_timestamp
from packages.common_common.tracker import Tracker
from packages.common_wechat.patches.filebox import FileBox
from settings import settings
from src.path import GENERATED_PATH


class Simulator(Tracker):
    
    def __init__(
        self,
        download_dir: Path = GENERATED_PATH,
        capture_type: Literal["direct", "crop", "frontend-download", "frontend-upload"] = "frontend-upload",
        input_type: Literal["send_keys", "js"] = 'js',
        headless=True
    ):
        """
        todo: avoid extra sending_keys via js input_type
        
        :param capture_type:
            1. direct 无法获得dpi=4的图像
            2. crop性能太差（要5秒）
            3. 要用frontend，本身基于 html-to-image 已经使用了 dpi=4
        :param input_type:
            1. send_keys 模拟手动发送，非常慢
            2. 要用 js
        :param dpi:
            1. 1-4, 4以上的截图质量没区别，但是耗时更长
            2. 当 capture_type 非 frontend 时，需要设置 dpi=4 才能最佳效果
        """
        super().__init__()
        
        dpi = 1 if capture_type == 'frontend-download' else 4
        
        self.dpi = dpi
        self.input_type = input_type
        self.capture_type = capture_type
        self.download_dir = download_dir
        self.track(f"init: dpi={self.dpi}, capture_type={self.capture_type}, input_type={self.input_type}, download_dir={self.download_dir}, headless={headless}")
        
        service = Service(ChromeDriverManager().install())
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--force-device-scale-factor={dpi}")  # ref: Selenium Can Make Hi-DPI, Retina Style Screenshots (Firefox and Chrome) - DEV Community, https://dev.to/simplecto/selenium-can-make-hi-dpi-retina-style-screenshots-firefox-and-chrome-37b9
        options.add_argument(f"--high-dpi-support={dpi}")  # This should match the scale factor
        prefs = {'download.default_directory': str(download_dir)}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options, service=service)
        self.track(f"driver started")
        
        self.driver.get(f'{settings.FRONTEND_BASEURL}/card/bgen')
        self.track("-- driver visited --")
    
    def _send(self, id: str, value: str):
        ele = self.driver.find_element(By.ID, id)
        if self.input_type == 'js':
            self.driver.execute_script('arguments[0].value=arguments[1];arguments[0].onchange;', ele, value)
            ele.send_keys(" ")
        elif self.input_type == 'send_keys':
            ele.send_keys(value)
        else:
            raise
        indeed = ele.get_attribute("value")
        self.track(f"inputted {id}, target={len(value)}, indeed={len(indeed)}, ok={len(value) == len(indeed)}")
    
    def _capture(self) -> FileBox:
        # 等待 action 按钮 ok 才可以开始导出图，否则不完整
        self.track("capturing")
        # ref: https://stackoverflow.com/a/44914767/9422455
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException)
        WebDriverWait(self.driver, 10, .1, ignored_exceptions=ignored_exceptions) \
            .until(lambda driver: driver.find_element(By.ID, "download-card").is_enabled())
        # todo: robuster wait download
        time.sleep(1)  # 目前不稳定，强制延时
        self.track("action buttons prepared")
        ele_preview = self.driver.find_element(By.ID, "card-preview")
        
        def wait_toast(type: Literal["upload", "download"]):
            self.driver.find_element(By.ID, f"{type}-card").click()
            # 如果不基于toast检测而基于Download text的话，则需要等待 .1 s
            toast_ele: WebElement = WebDriverWait(self.driver, 10, .1, ignored_exceptions=ignored_exceptions) \
                .until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".toast")))
            url = re.search(rf'{type}ed at (.*?)$', toast_ele.text)[1]
            logger.info(f"matched in toast: {url}")
            WebDriverWait(toast_ele, 3).until(EC.element_to_be_clickable((By.TAG_NAME, "button"))).click()
            return url
        
        if self.capture_type == "direct":
            fn = f"{get_current_timestamp(kind='s')}_{self.dpi}.png"
            ele_preview.screenshot(GENERATED_PATH.joinpath(fn))
            fn = wait_toast("download")
            return FileBox.from_file(self.download_dir.joinpath(fn).as_posix(), fn)
        
        # ref: https://chat.openai.com/c/6e606653-0f65-493a-9259-2599c723963e
        elif self.capture_type == "crop":
            fn = f"{get_current_timestamp(kind='s')}_{self.dpi}.png"
            location = ele_preview.location
            size = ele_preview.size
            x = location['x'] * self.dpi
            y = location['y'] * self.dpi
            width = x + size['width'] * self.dpi
            height = y + size['height'] * self.dpi
            bs = self.driver.get_screenshot_as_png()
            fs = Image.open(BytesIO(bs))
            element_screenshot = fs.crop((int(x), int(y), int(width), int(height)))
            element_screenshot.save(GENERATED_PATH.joinpath(fn))
            fn = wait_toast("download")
            return FileBox.from_file(self.download_dir.joinpath(fn).as_posix(), fn)
        
        elif self.capture_type == "frontend-download":
            fn = wait_toast("download")
            return FileBox.from_file(self.download_dir.joinpath(fn).as_posix(), fn)
        
        elif self.capture_type == "frontend-upload":
            url = wait_toast("upload")
            return FileBox.from_url(url, url)
        
        else:
            raise Exception("invalid capture type")
    
    def run(self, content: str, user_name: str = None, user_avatar: str = None) -> FileBox:
        try:
            data = json.loads(content)
            fn = f"{data['platformType']}_{data['platformId']}.png"
            self.track(f"\n>> running with card(fn={fn})", update=True)
            
            if user_name: self._send("card-user-name", user_name)
            if user_avatar: self._send("card-user-avatar", user_avatar)
            self._send("card-content", content)
            
            return self._capture()
        
        except Exception as e:
            logger.error(e)
    
    def _wait_exists(self, fn: str):
        fp = self.download_dir.joinpath(fn)
        for i in range(10):
            if fp.exists():
                self.track(f"{fp.as_uri()} existed({i})")
                return
            time.sleep(.2)
        raise Exception(f"{fp.as_uri()} not exist!")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.warning(f"exited: exc_type={exc_type}, exc_val={exc_val}, exc_tb={exc_tb}")
        self.driver.quit()
        logger.info("driver quited")


if __name__ == '__main__':
    download_dir = GENERATED_PATH.joinpath('images')
    shutil.rmtree(download_dir, ignore_errors=True)
    simulator = Simulator(headless=False, download_dir=download_dir)
    contents = [
        r'''{"platformId": "0e63739afeb928388f3eeecdb9793471", "platformType": "wxmpArticle", "sourceUrl": "http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&amp;mid=2247491674&amp;idx=1&amp;sn=0e63739afeb928388f3eeecdb9793471&amp;chksm=cecbcb20f9bc42364290c30b0d7868d6a119246e9f7378e2c8d0f645b2c6f8614d6c38c2cc3d&amp;mpshare=1&amp;scene=1&amp;srcid=0403OSXUdWuL7zGe5gLOUirm&amp;sharer_shareinfo=77b407be120eee88a999f46e8b3ddc42&amp;sharer_shareinfo_first=77b407be120eee88a999f46e8b3ddc42#rd", "author": {"id": null, "name": "有新Newin", "avatar": "http://wx.qlogo.cn/mmhead/Q3auHgzwzM4RANEFJicrdF4P3MaPCJNaRc9VrCKWCsyDlsZgzn6MPww/0"}, "time": "2024-04-03 03:42:23", "title": "GenAI 初创公司估值开始高峰回落", "cover": {"url": "https://mmbiz.qpic.cn/sz_mmbiz_jpg/wqO5B9doEHfI67Tia6IlicSBYk4tQYRspLEPtic4bWaea0PDHTzUupU5CoHywCUYBGibHXEe5yutLWL8L3TEyN7RicA/0?wx_fmt=jpeg", "width": null, "height": null}, "description": "近几个月来 AI 初创公司的估值可能已从高峰时期下降。三个月前， 外媒 Information 为 8 家主要提供消费者或企业服务的公司计算了此类估值倍数，这些服务与 LLM 有关......", "contentMd": "\\nGenAI 初创公司估值开始高峰回落\\n==================\\n\\n\\n近几个月来 AI 初创公司的估值可能已从高峰时期下降。三个月前， 外媒 Information 为 8 家主要提供消费者或企业服务的公司计算了此类估值倍数，这些服务与 LLM 有关。\\n===========================================================================================\\n\\n投资者将这些公司的估值定为 ARR（年度销售收入）的 83 倍，或投资时 MRR（月度销售收入）的 12 倍，有 3 家 AI 初创公司收入倍数平均为原始 8 家公司的 50%，这种下降归咎于营收的增长。\\n======================================================================================================\\n\\n当一家初创公司开始产生收入时，它们的未来销售倍数会从早期的高倍数快速滑落，因为那时它们几乎没有产生什么收入。根据 Meritech Capital 的数据，公开的软件公司平均未来收入在 7 倍。\\n\\n在最近几个月融资的三家 AI 初创公司包括 Perplexity AI，其收入倍数从上一轮融资的 150 下降到 67。投资者可能想知道 Perplexity 计划如何在仍在使用 Google 搜索和 Microsoft Bing 的数据时，挑战搜索引擎的现有巨头。甚至 Perplexity 的 CEO Aravind Srinivas 此前也表示，长期来看，该初创公司如何赚钱仍然不清楚，因为它很难利用 Google 使用的有利可图的广告模式。\\n\\n如何看待比上一代公司更早实现盈利的环境？[Srinivas 在与 Stripe CTO](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491528&idx=1&sn=84d0c349685acd82ffdeaa5c3fb06a8b&chksm=cec834b2f9bfbda4aa32a567dc8bc2e3e8165fc81b1fced64d394a2d5b40f6d24bf906f25733&scene=21#wechat_redirect) 的对话中表示，有了收入就不必继续筹集资金了，可以不断扩大顶部的漏斗，不断优化转化，以建立一个更可持续、更持久的企业，而不是一个短暂的时尚。如果真的想建立一个公司，最好尽快实现盈利，最好尽量提高效率，这也让早期创业者能够以后筹集更多的资金。当达到了良好的里程碑时，投资者会认为这确实会起作用。这也是为什么 Srinivas 将 Perpleixty 今年的目标定为 1 亿活跃用户。\\n\\n[微软联合举办的 GenAI 旧金山峰会2024火热来袭！斯坦福大学李佳教授确认出席，早鸟优惠至4月15日，抓紧时间～](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491658&idx=2&sn=7fa2a06f624bc7223346622530ae95a8&chksm=cecbcb30f9bc42269cefe6789e2c6cf92c5ecdade1cff28c3eba71695929519bdff075e8e998&scene=21#wechat_redirect)\\n===================================================================================================================================================================================================================================================================================\\n\\n[HeyGen 在近期获得了 4.4 亿美元估值](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491512&idx=1&sn=8c8be99528a3161d39f17be34eae25e0&chksm=cec834c2f9bfbdd424289c2d4dc9d027e07c939418267466b65e07e403c49ba4bab26233ca71&scene=21#wechat_redirect)，ARR 超过 2000 万美元，在许多商业化和融资两难的生成式 AI 初创公司中这种增长尤为突出，与许多其他生成式 AI 初创公司的估值倍数相比，其新估值约为前瞻收入的 22 倍。\\n\\nTogether.ai 在近期筹集超过 1 亿美元的新资金，使得公司仅在成立 20 个月后估值便超过 10 亿美元。\\n\\n[Together AI](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247490818&idx=1&sn=34544c484b72e1170741c70f47cfb864&chksm=cec83678f9bfbf6eea52b1a0a26a23dd626e66e5da78ad91956c4c622e6c17e71b84ae1dd4bc&scene=21#wechat_redirect) 由于租用 AI 芯片的高成本，可能面临着利润率的压力，其收入倍数在 2 月份为 38，高于 10 月份的 24，Together 也是海外投资人内部较有争议的 AI 新星之一，一些 VC 认为它在帮助开发者以低成本运行和训练开源模型方面取得了重要进展，但也有人更多地将其视为芯片转售商。\\n\\nCohere 是来自多伦多的 LLM 开发商，目前正在与包括加拿大养老基金 PSP 的投资者谈判，预计筹集超过 5 亿美元；与其他公司相比，Cohere 的业务发展不那么快，收入并不多，其最新一轮估值在 220 倍，为什么呢？\\n\\nCohere 是少数几个主要的非美国基础 LLM 开发商之一，加拿大急于支持本国的一个项目，可以参考 Mistral。尽管 Cohere 到目前为止收入增长缓慢，但 Cohere 也在 3 月推出了其最新模型，加速其销售增长。如果新一轮融资顺利，Cohere 将成为继 OpenAI 和 Anthropic 之后第三个获资最多的 LLM 初创公司，为接下来的业务扩张提供了更多时间和资金。\\n\\n此外，上周 [Accel 领投 27 岁华人创立的铲子公司 Scale AI，估值 130 亿美元！附 Accel 合伙人最新一二级市场洞察](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491658&idx=1&sn=73796b84b941694278f56d8f3ec5a8a8&chksm=cecbcb30f9bc422628f1a80a50fdda85626b7372ef27cb4dd2f46f21bcf5c21707ab00195f75&scene=21#wechat_redirect)。去年，Scale AI 的收入超过 6.75 亿美元，较前一年增长约 150%，新的增长促使 27 岁的 Scale AI 创始人 Alexandr Wang 加速扩张并寻求新的融资。\\n===========================================================================================================================================================================================================================================================================================================================================================================================\\n\\nAccel 表示，更感兴趣的是像 Scale 这样的“镐和铲”业务，Scale AI 是许多模型背后的数据引擎，不仅是基础玩家，也是尝试为他们的垂直应用调整的人。Accel 认为，Scale AI 将会有远远超过 5 大模型的重要客户。\\n======================================================================================================================\\n\\nReference：\\n\\nhttps://www.theinformation.com/articles/ai-valuations-may-be-coming-down-to-earth-a-glimpse-of-openais-search-engine?rc=z9mejq\\n\\n**Newin 行业交流群******下方扫码加入“有新Newin”读者交流群👇******最新活动****最新资讯****近期精选*** [红杉美国 AI 峰会最新洞察｜生成式 AI 一年营收走完 SaaS 十年的路；未来软件替代服务，数万亿可能仅是起点](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491599&idx=1&sn=20d6bfb9c3f40ba893f3cb3064a495ec&chksm=cecbcb75f9bc42632fa0f79b999b916e6d822bca80ee33c6f43a85288313b9fcc0b33764510c&scene=21#wechat_redirect)\\n* [Mistral CEO 红杉美国分享：五年后，任何人都能创建 AI 自主代理，开发者与用户界限变得模糊](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491652&idx=1&sn=2ef8be034d597b489fc7c5d6e1641835&chksm=cecbcb3ef9bc4228232bf641cd89dfafa6e31cf28129087ced379ad217d8106bf0b011de0c1b&scene=21#wechat_redirect)\\n* [吴恩达红杉美国 AI 峰会谈 Agent Workflow 以及 4 种主流设计模式，相比 LLM 更强调迭代与对话](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491624&idx=1&sn=c5ec7ccf1de09cb976c3522791a4de70&chksm=cecbcb52f9bc42444a436d66502253e63c8b2b816327de38c1b5151c3c157dab01f8d7cd33d4&scene=21#wechat_redirect)\\n* [Andrej Karpathy 美国红杉资本最新对谈，达到 AGI 或需全新架构](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491565&idx=1&sn=b82d93592babf9f8d413ad83be4f5927&chksm=cec83497f9bfbd819a2e750b222dbf32c065dde979db0e11b1a1e46cb29f3db019752948d86e&scene=21#wechat_redirect)\\n* [YC 创始人 Paul Graham 最新分享｜创立下一个谷歌，学校没有教给学生的创业三要素 —— 技术、项目与合伙人](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491541&idx=1&sn=abbe9e0702d8f1334dcba66d06c2ddee&chksm=cec834aff9bfbdb91332abaa34a3ae4a47aefcb5f2af183ec10b292068039bfe0dce75da46ba&scene=21#wechat_redirect)\\n* [今年目标1亿活跃用户！Perplexity联手Arc浏览器对抗Google背后产品逻辑](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491528&idx=1&sn=84d0c349685acd82ffdeaa5c3fb06a8b&chksm=cec834b2f9bfbda4aa32a567dc8bc2e3e8165fc81b1fced64d394a2d5b40f6d24bf906f25733&scene=21#wechat_redirect)\\n* [刚刚，华人创办的 AI 视频生成公司 HeyGen 最新估值 4.4 亿美元！BenchMark 领投](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491512&idx=1&sn=8c8be99528a3161d39f17be34eae25e0&chksm=cec834c2f9bfbdd424289c2d4dc9d027e07c939418267466b65e07e403c49ba4bab26233ca71&scene=21#wechat_redirect)\\n* [对话 ChatGPT 负责人｜ChatGPT 增强了每个人的技能集，未来公司会变得更小，但会有更多这样的公司](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491308&idx=1&sn=f8de478d3bbf532992de7d731168211f&chksm=cec83596f9bfbc8020b5b621374e61802b96d8bcfa28702c89ee49e5efb5dd757f0ace602d7c&scene=21#wechat_redirect)\\n* [【3.2万字实录】Sam Altman 最新专访｜董事会、马斯克诉讼、GPT-5、Sora、AGI、7 万亿美元......](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491447&idx=2&sn=5a7af1e4429d80927a558e3532d96f03&chksm=cec8340df9bfbd1bdc22d06eb3131866638cc2785f1cc5035a48cb4d9367ed1ec12466ec6ce3&scene=21#wechat_redirect)\\n* [Nvidia GTC 大会 CEO 黄仁勋推最强 AI 芯片 Blackwell 实现万亿参数 AI](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491424&idx=1&sn=64f8d7f92af2446c18db82b8551b47ba&chksm=cec8341af9bfbd0ccbec5b273b5f235e0409efd5306d238f5fd84e2f334eb430fc02c41cd075&scene=21#wechat_redirect)\\n* [纳德拉对话挪威财富基金 CEO，谈 AI 范式转变对经济影响与科技支出](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491360&idx=1&sn=1f786e84f3d4c3d8aac695980a1ac694&chksm=cec8345af9bfbd4ce0935fb5f04515fe0f56d8e49725e350f51b1e4f785ac98aea4d83f7a3ea&scene=21#wechat_redirect)\\n* [刚刚，a16z 发布了 GenAI 消费应用 Top100 报告，涵盖 Web 端与移动端](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491356&idx=1&sn=36a39b0367f292f329bcdd82d6a90ebd&chksm=cec83466f9bfbd701c93a6f31f469078019053a0e18f36966eeafd932e1df36f66b88c50ccb1&scene=21#wechat_redirect)\\n* [黄仁勋：未来十年算力将再提高 100 万倍，液冷成 AI 算力下一趋势领域](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491284&idx=1&sn=450a73f98cc01bc93473269b5a206f18&chksm=cec835aef9bfbcb88456ba2d5889629d83931715db75ef480d989afbd12e59942a599576b602&scene=21#wechat_redirect)\\n* [Rabbit CEO 谈苹果 AI 新动作与竞争｜来回切换 App 很糟糕，R1 是成本与体验的平衡，99% 创业公司会死掉！](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491170&idx=1&sn=240aea596ee5ff5c254b707e64a0af38&chksm=cec83518f9bfbc0ed618ff829aa18f97f990409169fcd2dd211ef9dde27cec00b458955cf1d4&scene=21#wechat_redirect)\\n* [刚刚！马斯克正式起诉 Sam Altman（附 1.2 万字指控细节）](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491156&idx=1&sn=b27ebc8d2079d0b71a10d172b2b721a3&chksm=cec8352ef9bfbc38e2c301dd5e0dc2b8e1d1a4256f91bccf75bf2106bf382ee9e06ea1467030&scene=21#wechat_redirect)\\n* [ARK 对话 Figure 创始人｜最新估值 20 亿美元！为扩展人类能力，未来将数十亿台机器人推向世界](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491147&idx=1&sn=f0889b18c8e332678eb13b04de338016&chksm=cec83531f9bfbc2711b1ea751b6ffaf975f5f67c24d1f019163cce9c9c94002b4abd73feb1d7&scene=21#wechat_redirect)\\n* [DeepMind CEO 最新《纽约时报》专访：AGI 将使能源变得廉价甚至免费，货币性质也将发生转变](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491106&idx=1&sn=2075965b4af23c9ffb63790ab03402db&chksm=cec83558f9bfbc4e661bab07c326f0b6479d5e22cd97ed3f32f1bf466a2a7f73393c9bbcc972&scene=21#wechat_redirect)\\n* [OpenAI 首位投资人 Khosla 最新洞察：AI 使人机交互发生根本性转变，软件将进一步适应人类](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247491097&idx=1&sn=c95a97d50251a40cc3c1203881e6fa23&chksm=cec83563f9bfbc75a0ca46202d4b16c6ff4b2f670d156c4a2d5645dd46013245291b8f2a556d&scene=21#wechat_redirect)\\n* [扎克伯格最新对谈：智能手机不会消失，AR 会是主流移动计算设备，XR 则是桌面计算设备，生成式 AI 实现人机交流](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247490932&idx=1&sn=7809037ea8b952392a7d4b9227efebbf&chksm=cec8360ef9bfbf18bda9c8a2a51102b96bb6f12178e2a37863373ebdf2edfdf35cd0308ad077&scene=21#wechat_redirect)\\n* [YC 发布了 2024 年关注的 20 个创业方向，覆盖 AI、机器人、空间计算、企业服务、开源软件、自动化....](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247490919&idx=1&sn=86b3e5aac7d5680a8c4341deb0a02e61&chksm=cec8361df9bfbf0baa52e34926b1400d061b82ddd2d315045ccd84858987a76e37f2efdfc914&scene=21#wechat_redirect)\\n* [英伟达创始人 CEO 黄仁勋最新 “世界政府峰会” 讲话：7 万亿美元可以买下所有 GPU...6 周后将见证下一代 AI...](http://mp.weixin.qq.com/s?__biz=Mzg3NDkyMTQ5Mw==&mid=2247490804&idx=1&sn=5a9aa60c1fe78c332bd7c1063883b0d0&chksm=cec8378ef9bfbe98a10dee369834c9409f303c394a456da7d39a50a1f005b0fc79e3b020753b&scene=21#wechat_redirect)\\n\\n  \\n  \\n  \\n\\n\\n", "contentSummary": {"modelType": "gpt-4", "result": "<title>AI初创公司估值从高峰回落</title>\n<description>近几个月，AI初创公司的估值可能已从高峰时期下降。投资者将这些公司的估值定为年度销售收入的83倍，或投资时月度销售收入的12倍，有3家AI初创公司收入倍数平均为原始8家公司的50%，这种下降归咎于营收的增长。</description>\n<mindmap>\n- AI初创公司估值下降\n  - 投资者估值基于年度销售收入或月度销售收入\n  - 3家AI初创公司收入倍数下降50%\n- 营收增长导致估值下降\n  - 初创公司开始产生收入时，未来销售倍数会快速滑落\n  - 公开的软件公司平均未来收入在7倍\n- AI初创公司融资情况\n  - Perplexity AI收入倍数从150下降到67\n  - HeyGen近期获得4.4亿美元估值，ARR超过2000万美元\n  - Together.ai筹集超过1亿美元新资金，估值超过10亿美元\n  - Cohere预计筹集超过5亿美元，最新一轮估值在220倍\n</mindmap>\n<comment>AI初创公司的估值下降反映了市场对其盈利能力的重新评估，这可能会对初创公司的融资和发展产生影响。然而，这也可能是一个健康的调整，使得公司更加注重实际的盈利能力，而不仅仅是依赖投资者的资金。</comment>\n<tags>AI, 初创公司, 估值</tags>"}}''',
        r'''{"platformId": "7ece597c8aba94854bbabe4af7c8aedb", "platformType": "wxmpArticle", "sourceUrl": "http://mp.weixin.qq.com/s?__biz=MzU0MDQ1NjAzNg==&amp;mid=2247579300&amp;idx=1&amp;sn=7ece597c8aba94854bbabe4af7c8aedb&amp;chksm=fa0e3f9ed0196d9730362323586c409acb71e3e39d212db7309313637aa0caea62c67c5763a6&amp;scene=0&amp;xtrack=1#rd", "author": {"id": null, "name": "机器学习算法那些事", "avatar": "http://wx.qlogo.cn/mmhead/Q3auHgzwzM6E8G0xhFnw8kiaDohibeMsF83Rur5ntFdoaNw7fjtgRV2Q/0"}, "time": "2024-04-03 06:19:52", "title": "“计算机视觉女神”被IEEE期刊封杀", "cover": {"url": "https://mmbiz.qpic.cn/mmbiz_jpg/hN1l83J6Ph9Sj4T2vEicZwfgXxfoAyqt2FnjEBSw5P3XwYGRB1juOOG6eNMXhHjFQ7z6ceQDjsP1KP8fgicAnrIg/0?wx_fmt=jpeg", "width": null, "height": null}, "description": "不再接收含该图的论文", "contentMd": "\\n“计算机视觉女神”被IEEE期刊封杀\\n==================\\n\\n\\n来源：量子位\\n\\n计算机学术界的女神“**Lenna**”被IEEE“封杀”了——\\n\\nIEEE计算机协会宣布，**4月1日起不再接收包含该图像的论文**。\\n\\n###### \\n\\n###### **△**Lenna图\\n\\nIEEE技术&会议活动副主席Terry Benzel在邮件里这样写道：\\n\\n\\n> IEEE本着坚持促进开放、包容及公平文化的承诺，同时尊重照片主体Lena Forsén本人的意愿，决定不再接收包含Lenna图像的论文。\\n\\n也就是说，之后委员会或审稿人会特地留意论文中是否有这张图，如果有的话，会要求作者用替换图片。\\n\\n“Lenna图”的时代彻底结束了？要知道，这张图曾经的火爆程度belike：\\n\\n  \\n\\n\\n“计算机视觉女神”\\n---------\\n\\nLenna图最初是登在**1972年**11月期的《花花公子》（Playboy）杂志上的一张裸体插图，由摄影师Dwight Hooker拍摄，图中主体是瑞典模特**Lena Forsén**。\\n\\n当时，为了方便英语读者读准瑞典语“Lena”的发音，《花花公子》使用了“Lenna”这一名字。\\n\\nLenna成为高分辨率彩色图像处理研究标准图的历史，在2001年5月的IEEE ComSoc通讯文章中被讲述：\\n\\n1973年的六七月份，时任南加州大学电气工程助理教授的**Alexander Sawchuk**及其团队，包括一名研究生和SIPI实验室管理人，正急切地寻找一张适合会议论文使用的高质量图片。\\n\\n他们的目标是找到一张既有光泽又能展现出良好动态范围的图像，而且最好是一张人脸图片。\\n\\n恰巧这时有人带着一本最新版的《花花公子》杂志走了进来。里面的Lenna图，被研究人员选中。\\n\\n他们将插图放到Muirhead有线传真扫描仪的光鼓上进行扫描。Muirhead的分辨率为固定的100LPI，而研究人员希望得到一幅512×512的图像，所以他们将扫描范围定在上部的5.12英寸，这样恰好裁剪到人物的肩膀位置，去除了裸体的部分。\\n\\n由此，一张512x512的Lenna测试图就诞生了。\\n\\n这张图在上世纪七八十年代的传播范围有限，最初仅是在美国各高校实验室之间流行。但到了1991年7月，Lenna图与另一张流行的测试图Peppers一起出现在计算机视觉领域的**《Optical Engineering》**杂志封面上，引起了大家的广泛注意。\\n\\nLenna图备受喜欢的原因大概有这么几点。\\n\\n首先从技术上来讲，Lenna图有丰富的细节、明暗对比，同时也有平滑的过渡区域，而这很考验图像压缩算法的能力。\\n\\n众所周知，数字图像就是一个个像素点排列而成。而在压缩的时候，这些像素点都会被转化成频率信号。\\n\\n像素点之间差异大的区域，通常也就是细节丰富的区域，转化后对应高频信号，比较难处理；反过来像素点之间差异小的平滑过渡区域，就对应低频信号，处理起来也相对简单。\\n\\n一个好的压缩算法，高频和低频信号都得处理好。这两种信号，Lenna都有，分配比例还很恰当。\\n\\n其次，Lenna是一张漂亮小姐姐的照片，懂得都懂。但除此之外，还有一个更重要的原因：**人眼对人脸非常敏感**。\\n\\n你可能认不出两只二哈的脸有什么区别，但一个人的表情即使只有一丢丢变化，你都能一眼发觉。\\n\\n对图像压缩来说，相较于其他图像，人会更容易发觉人像在压缩前后的差异，所以也就更容易比较不同算法的好坏。\\n\\n正是由于以上种种优点，Lenna很快成了图像处理的标准测试图片。\\n\\n根据国外一个网站统计，91年后Lenna在互联网上的出现次数开始猛长。到了1996年，业界顶级期刊IEEE图像处理汇刊里，竟然有接近三分之一的文章都用到了Lenna。\\n\\n光在1999年的一期《IEEE图像处理汇刊》中，Lenna就被用于三篇独立研究中，21世纪初它还出现在了科学期刊中。\\n\\n由于Lenna在图像处理界被广泛接受，Lena Forsén本人受邀成为了1997年成像科学与技术学会 （IS&T） 第50届年会的嘉宾。2015年，Lena Forsén也是IEEE ICIP 2015晚宴的嘉宾，主持了最佳论文奖颁奖仪式。\\n\\nLenna图的消逝\\n---------\\n\\n不过，随之而来的还有大伙儿对这张图的批评。最大问题，就在于这张照片来源于有“物化女性”之嫌争议的《花花公子》。\\n\\n1999年，在一篇关于计算机科学中男性占主导地位原因的论文中，应用数学家Dianne P. O’Leary写道：\\n\\n“在图像处理中使用的暗示性图片……传达了讲师只迎合男性的信息。例如，令人惊讶的是，Lenna图像图像至今仍作为示例在课程中使用，并作为测试图片发表于学术期刊。”\\n\\n2015年，一个美国高中生在《华盛顿邮报》上写了一篇文章，文中叙述了自己作为一个女生，在计算机课上看到这张照片后感到不适，“我不理解，为什么一所先进的理工学校，在教学中会用一张花花公子的封面？”\\n\\n虽然这只是一篇高中生写的文章，但却在学界引起了巨大的震动。\\n\\n由于种种争议，2018年， Nature Nanotechnology杂志宣布禁止在论文提交中使用Lenna图像。\\n\\n至于Lena Forsén，2019年《连线》一篇文章中写道，Forsén并没有对这张图片心怀怨恨，但她对当初没有为此获得更好的报酬感到遗憾，曾表示“我真的为那张照片感到骄傲”。\\n\\n###### \\n\\n###### **△**Lena Forsén重拍当年照片\\n\\n但2019 年，Creatable和Code Like a Girl制作了一部名为“Losing Lena”的纪录片。Lena Forsén表示：\\n\\n\\n> 我很久以前就退出了模特界，现在也该退出科技界了。我们可以在今天做出一个简单的改变，为明天创造一个持久的改变。让我们承诺失去我。\\n\\n现在看来，这一承诺正在兑现。\\n\\n除了上面所讲的争议，有网友认为Lenna图在当今这个时代的意义也跟以往大有不同了。\\n\\n\\n> 不同于以往，当今几乎人人都可轻易使用一台好的相机。大多数精力应投入于创造合适的光照条件和挑选满足特定标准的拍摄对象。此外，一个精心设计的计算机生成图像也能满足需求。\\n\\n参考链接：https://arstechnica.com/information-technology/2024/03/playboy-image-from-1972-gets-ban-from-ieee-computer-journals/\\n\\n\\n\\n", "contentSummary": {"modelType": "gpt-4", "result": "<title>IEEE期刊禁止使用“计算机视觉女神”Lenna图</title>\n<description>IEEE计算机协会宣布，不再接收包含Lenna图像的论文。Lenna图源自1972年《花花公子》杂志的一张插图，由于其丰富的细节和明暗对比，以及人眼对人脸的敏感性，成为了图像处理的标准测试图片。然而，由于其来源于有“物化女性”之嫌的《花花公子》杂志，引发了争议。</description>\n<mindmap>\n- Lenna图的起源\n  - 1972年《花花公子》杂志插图\n  - 摄影师Dwight Hooker拍摄，主体是瑞典模特Lena Forsén\n- Lenna图的流行\n  - 丰富的细节、明暗对比\n  - 人眼对人脸的敏感性\n  - 1991年出现在《Optical Engineering》杂志封面\n- Lenna图的争议\n  - 来源于有“物化女性”之嫌的《花花公子》杂志\n  - 2018年，Nature Nanotechnology杂志禁止使用Lenna图像\n  - 2021年，IEEE计算机协会禁止使用Lenna图像\n</mindmap>\n<comment>尽管Lenna图在图像处理领域有其独特的价值，但其来源和使用环境的争议也不容忽视。IEEE的决定是对尊重和公平的重要表现，也是对科研环境更加开放、包容的追求。</comment>\n<tags>IEEE, Lenna图, 计算机视觉</tags>"}}''',
        r'''{"platformId": "14c1902baabda97b1a0891469ed272a1", "platformType": "wxmpArticle", "sourceUrl": "http://mp.weixin.qq.com/s?__biz=MzA4NjcyMDU1NQ==&amp;mid=2247848147&amp;idx=1&amp;sn=14c1902baabda97b1a0891469ed272a1&amp;chksm=9fcbb997a8bc308167197f6add044b63ea5a0437c8e3a73e3a4b3edc8e686138692795ffaf6d&amp;mpshare=1&amp;scene=1&amp;srcid=0406CRHwlWOTHuD151lbUgPa&amp;sharer_shareinfo=8c3f94cfc415063a593687e961bbfe64&amp;sharer_shareinfo_first=8c3f94cfc415063a593687e961bbfe64#rd", "author": {"id": null, "name": "KnowYourself", "avatar": "http://wx.qlogo.cn/mmhead/Q3auHgzwzM5aljzuLBOQdjWhFAzrDMicxSczxFAicb9gv6ib7mNaAY1Gg/0"}, "time": "2024-04-06 10:00:44", "title": "符合这4个特质的人，拥有治愈他人的珍贵天赋。", "cover": {"url": "https://mmbiz.qpic.cn/sz_mmbiz_jpg/Mz0ovPEFMRIv3nPR10q1Z4LMZELdOcqGUh4pGyHFk9vwYQibMeoBB0XAiaBvVgXFySmzwotpStct3YCdRCZUYMQw/0?wx_fmt=jpeg", "width": null, "height": null}, "description": "《0基础心理助人体验计划 · 3日入门班》", "contentMd": "\\n符合这4个特质的人，拥有治愈他人的珍贵天赋。\\n======================\\n\\n\\n  \\n\\n\\n  \\n\\n\\n在KY收到的众多评价中，有一个颇为触动我们的反馈：\\n\\n  \\n\\n\\n\\n> “真的很喜欢和你一起聊愈的过程，这是今年来给我最多力量的一件事。\\n> \\n>   \\n> \\n> \\n> 无论是哭还是笑，都很安心、很自在；无论你带我进入哪个阶段，我都觉得自己在成长。”\\n\\n  \\n\\n\\n这位聊愈师看到这段话时，她也很感慨，**虽然成为聊愈师****仅半年****，但在这份工作里她已经收获了****强烈的成就感**。看起来是她给予别人心理关怀和指引，但每次对话的过程，**对她自身而言也是一次自我反思与成长**。  \\n\\n\\n  \\n\\n\\n**聊愈师与聊愈来访，是一种双向治愈、双向奔赴的关系。**\\n\\n  \\n ****什么样的人适合成为聊愈师****  \\n\\n\\n有很多喜欢聊愈、喜欢KY的同学都咨询过这个问题，从个性特质来看，符合这几个特点的人更适合从事**心理助人、心理疗愈**类工作：\\n\\n  \\n\\n\\n**1. 善于洞察，富有同理心和耐心**\\n\\n  \\n\\n\\n洞察力强、同理心强（高敏感者的常见特质）的人，容易被他人或文艺作品中角色的情感打动，**擅长设身处地理解别人的情绪，善于发现微小细节所暗示的含义**（如微表情、语气等）。\\n\\n  \\n\\n\\n**2. 有包容多元的价值观与乐观开放的态度**\\n\\n  \\n\\n\\n聊愈师的日常工作就是与大量形形色色的人交往，接触多元的文化背景、生活习惯、性向等。优秀的助人者即使面对不符合价值观的事物，也不会批判指责，而是**能以包容、开放的态度面对个体的复杂性**。\\n\\n  \\n\\n\\n**3. 喜欢1v1深入沟通，用专业知识帮助别人**\\n\\n  \\n\\n\\n比起泛泛之交，有些人更加**偏好深度的人际联结**，在心灵交流中触摸他人的灵魂，给予其共情和理解。通常ta们也都**高度热爱探索自我**，对内心世界、对心理学有强烈的兴趣。\\n\\n  \\n\\n\\n**4. 有终身学习的准备**\\n\\n  \\n\\n\\n心理学研究永远与时俱进，心理学人也是如此。\\n\\n  \\n\\n\\n他们愿意不断地去**更新知识、积累经验**，去探索和理解人性的边界，也许入行只要短短数月，但若要把心理助人作为**终身事业，则需要数年不断的耕耘****，收获也会加倍丰厚。**\\n\\n  \\n\\n\\n卡尔 · 罗杰斯说：**“当有人真正倾听你，不对你评头论足，不替你担惊受怕，也不想改变你，这感觉真好啊。”**\\n\\n  \\n\\n\\n如果你也想成为这样的助人者，但还存有疑问如：还有哪些特质适合从事这行？怎样的培养路径更加适合我？应该学些什么？收入回报如何？……\\n\\n  \\n\\n\\nKnowyourself的**《0基础心理助人体验计划 · 3日入门班》**能够解答你的种种疑惑——在深入浅出地教会你**如何用心理学处理生活问题、实现个人成长**的同时，也带你**快速探索充满前景和机遇的心理行业**。\\n\\n  \\n****👇点击图片即刻报名👇****  \\n ****实用易懂，边学边练\\n\\n覆盖95%生活场景****  \\n**这是一门怎样的体验课？**首先可以跟大家保证的是，这门课和市面上的多数心理课程不同，这门课是真心想要让你“学了就会，会了就用”，所以最大的优势在于**实用+易学**。  \\n首先，这门课非常符合**成年人的学习特征**。和孩子不同，我们想要学心理学更多是**出于对实际问题的解决需求****：怎么缓解焦虑、沮丧？如何走出前段恋情的创伤？怎么调节职场压力，处理人际关系？……**  \\n因此，整个课程内容因此这套体验课**从心理学的应用出发**，结合**接地气且生活化的实例讲解，通过“应用实践”学习“心理学理论”**。  \\n  \\n仅在我们的体验课中，就覆盖了**原生家庭、恋爱婚姻、负面情绪**等多个议题的案例分析，在**前2天**里带大家**重点分析****6个高度真实的生活化案例**，从**助人者的第一视角**切入，帮助大家学习专业心理助人技巧和工作思路。  \\n通过课程的学习和对应的练习，能有助于帮你判断自身是否具备成为聊愈师的潜质。  \\n  \\n  \\n  \\n****行业专家&一线从业者********分享一手信息与经验****  \\n这次会由KY的**心理聊愈服务专业负责人****孙露纯**，与**资深从业者全职聊愈师****西野**作为课程讲师，带领大家体验心理助人技术的学习和应用。  \\n  \\n除此以外，ta们也会与大家分享自己在**心理学从业的一手信息和经验**，比如：* **进入心理行业的契机是什么，遇到什么困难？**\\n* **如何挑选适合自己的路径进入心理行业？未来如何发展？**\\n* **全职聊愈师的一天是如何度过的？**\\n* **在心理行业有什么收获？（收入/成长/生活变化等）……**\\n\\n对于想要进一步探索聊愈师职业的人来说，不容错过！  \\n ****高增量心理行业\\n\\n1v1提供执业评估****数据显示，**中国平均每百万人口中，仅有20人能提供心理健康服务****，而美国有1000人，是中国的****50倍**。  \\n  \\n**而且，这是一门越老越吃香的事业，它不仅能给你助人的成就感，也能让你积累的每点人生经验都发挥充分的作用**。  \\n如果通过学习课程，你能解答这些疑问——心理学和每个人的生活到底有什么关系？怎么用它去解决自己实际面对的种种困境，甚至去帮助身边的人？如何以更成熟的、心理学的视角去看待外部世界？……  \\n那你已经**半只脚踏入了心理行业，拥有做一份心理副业甚至转行的可能性**。 ****现在报名体验课，我们还将提供1v1心理行业执业评估与指导，帮你快速建立自身定位，定制更适合你的心理行业成长路径。**\\n\\n  \\n\\n\\n  \\n\\n\\n  \\n\\n\\n****什么人\\n\\n适合学这门课******如果你还在纠结，这门课**新手小白是否能够学明白**，如果你还在犹豫，**已经是心理/社工专业者**，这门课是否有价值；如果你在思考，仅仅**想学习人际沟通，或改善自己的心理问题**，适不适合学这门课……  \\n  \\n**答案都是——YES！**  \\n我们欢迎每个想要用过心理学自助、助人的求学者，符合以下特质的KYer，也承诺你们在这门课中一定会学有所得！  \\n  \\n  \\n  \\n**19.9元****一键开启体验之旅**  \\n**《0基础心理助人体验计划 · 3日入门班》**  \\n  \\n√ **6+**案例第一视角分析√ **2天**趣味练习 思考实践√**1个**高质量社群√ **1v1**高效执业评估  \\n****👇点击图片即刻报名👇******小提示：购买了课程的KYer，一定要记得根据提示添加专属【**心理职业规划师**】，领取课程与相关权益喔！**  \\n  \\n\\n\\n**广告**  \\n  \\n  \\n  \\n  \\n\\n\\n", "contentSummary": {"modelType": "gpt-4", "result": "<title>成为聊愈师的四大特质</title>\n<description>文章讨论了成为聊愈师需要的四大特质：善于洞察、富有同理心和耐心；有包容多元的价值观与乐观开放的态度；喜欢1v1深入沟通，用专业知识帮助别人；有终身学习的准备。同时，文章也推荐了一门心理助人的体验课程。</description>\n<mindmap>\n- 成为聊愈师的四大特质\n  - 善于洞察，富有同理心和耐心\n  - 有包容多元的价值观与乐观开放的态度\n  - 喜欢1v1深入沟通，用专业知识帮助别人\n  - 有终身学习的准备\n- 推荐心理助人体验课程\n  - 课程内容实用易学\n  - 行业专家分享一手信息与经验\n  - 提供1v1心理行业执业评估与指导\n</mindmap>\n<comment>文章深入浅出地解析了成为聊愈师所需的特质，对于有志于从事心理助人工作的人来说，具有很好的参考价值。同时，推荐的心理助人体验课程也为读者提供了实践的机会。</comment>\n<tags>心理咨询,聊愈师,心理助人</tags>"}}'''
    ]
    
    for content in contents:
        simulator.run(content, "mark", "http://wx.qlogo.cn/mmhead/Q3auHgzwzM4RANEFJicrdF4P3MaPCJNaRc9VrCKWCsyDlsZgzn6MPww/0")
        # time.sleep(2)
