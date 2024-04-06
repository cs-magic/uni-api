import os.path
import re
import shutil
import time
from io import BytesIO
from typing import Literal

from PIL import Image
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from packages.common_datetime.utils import get_current_timestamp
from packages.common_general.tracker import Tracker
from settings import settings
from src.path import GENERATED_PATH


class Simulator(Tracker):
    
    def __init__(
        self,
        download_dir: str = str(GENERATED_PATH),
        capture_type: Literal["direct", "crop", "frontend"] = "frontend",
        input_type: Literal["send_keys", "js"] = 'js',
        dpi: int = 1,
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
        
        self.dpi = dpi
        self.input_type = input_type
        self.capture_type = capture_type
        self.download_dir = download_dir
        self.track(f"init: dpi={self.dpi}, capture_type={self.capture_type}, input_type={self.input_type}, download_dir={self.download_dir}")
        
        service = Service(ChromeDriverManager().install())
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--force-device-scale-factor={dpi}")  # ref: Selenium Can Make Hi-DPI, Retina Style Screenshots (Firefox and Chrome) - DEV Community, https://dev.to/simplecto/selenium-can-make-hi-dpi-retina-style-screenshots-firefox-and-chrome-37b9
        options.add_argument(f"--high-dpi-support={dpi}")  # This should match the scale factor
        prefs = {'download.default_directory': download_dir}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options, service=service)
        self.track(f"driver started")
        
        self.driver.get(f'{settings.FRONTEND_BASEURL}/card/gen')
        self.track("-- driver visited --\n")
        
        self.t = '%E6%8A%A5%E4%BB%B7%E5%A4%AA%E4%BE%BF%E5%AE%9C%EF%BC%8C%E4%B8%AD%E5%9B%BD%E9%AB%98%E9%93%81%E8%A2%AB%E8%B8%A2%E5%87%BA%E4%BF%9D%E5%8A%A0%E5%88%A9%E4%BA%9A%EF%BC%81.png'
    
    def _send(self, id: str, value: str | None):
        ele = self.driver.find_element(By.ID, id)
        if value:
            if self.input_type == 'js':
                self.driver.execute_script('arguments[0].value=arguments[1];arguments[0].onchange;', ele, value)
                ele.send_keys(" ")
            elif self.input_type == 'send_keys':
                ele.send_keys(value)
            else:
                raise
        else:
            logger.debug("-- skipped")
        # indeed = ele.get_attribute("value")
        # self.track(f"inputted {id}, target={len(value)}, indeed={len(indeed)}, ok={len(value) == len(indeed)}")
    
    def _capture(self):
        # 等待 action 按钮 ok 才可以开始导出图，否则不完整
        WebDriverWait(self.driver, 10, .1).until(lambda driver: driver.find_element(By.ID, "download-card").is_enabled())
        ele_preview = self.driver.find_element(By.ID, "card-preview")
        fp = GENERATED_PATH.joinpath(f"{get_current_timestamp(kind='s')}_{self.dpi}.png").__str__()
        if self.capture_type == "direct":
            ele_preview.screenshot(fp)
        
        # ref: https://chat.openai.com/c/6e606653-0f65-493a-9259-2599c723963e
        elif self.capture_type == "crop":
            location = ele_preview.location
            size = ele_preview.size
            x = location['x'] * self.dpi
            y = location['y'] * self.dpi
            width = x + size['width'] * self.dpi
            height = y + size['height'] * self.dpi
            bs = self.driver.get_screenshot_as_png()
            fs = Image.open(BytesIO(bs))
            element_screenshot = fs.crop((int(x), int(y), int(width), int(height)))
            element_screenshot.save(fp)
        
        elif self.capture_type == "frontend":
            self.driver.find_element(By.ID, "download-card").click()
            css_selector = '.toaster div[data-title]'
            # 如果不基于toast检测而基于Download text的话，则需要等待 .1 s
            ele_downloaded = WebDriverWait(self.driver, 10, .1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            fp = GENERATED_PATH.joinpath(re.search(r"at (.*?)$", ele_downloaded.text)[1])
        else:
            raise
        self.track(f"downloaded --> {fp}")
    
    def run(self, content: str, user_name: str = None, user_avatar: str = None):
        try:
            self.track(f"running user={user_name} content={content[:20]}...")
            GENERATED_PATH.joinpath(self.t).unlink(missing_ok=True)
            self._send("card-user-name", user_name)
            self._send("card-user-avatar", user_avatar)
            self._send("card-content", content)
            self._capture()
            
            self._test_wait_move()
        except Exception as e:
            logger.error(e)
        finally:
            self.track(f"-- done --\n")
    
    def _test_wait_move(self):
        for i in range(3):
            if os.path.exists(GENERATED_PATH.joinpath(self.t)):
                shutil.move(GENERATED_PATH.joinpath(self.t), GENERATED_PATH.joinpath(f'{time.time()}.png'))
                # self.track(f"moved ({i})")
                return
            time.sleep(.2)
        self.track("failed to move")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.warning(f"exited: exc_type={exc_type}, exc_val={exc_val}, exc_tb={exc_tb}")
        self.driver.quit()
        logger.info("driver quited")


if __name__ == '__main__':
    simulator = Simulator()
    content = r'''{"id":"6F10r-G","createdAt":"2024-04-05T13:31:23.967Z","updatedAt":"2024-04-05T14:34:52.956Z","platformType":"wxmpArticle","platformId":"7176a5c338a0a4d2f53d8c96c73460a6","platformData":null,"sourceUrl":null,"author":{"id":null,"name":"牲产队","avatar":"http://wx.qlogo.cn/mmhead/Q3auHgzwzM7fVxzEwUEk7cYsTVU6ZHWJkUtoh2cPVnREfGS2Igevhg/0"},"time":"2024-03-31T22:51:26.000Z","title":"报价太便宜，中国高铁被踢出保加利亚！","description":"走廉价路线，不利于共同富裕。","cover":{"url":"https://mmbiz.qpic.cn/mmbiz_jpg/iazG1Weex64rJ2IFBM63RXM9tZxbTEQ402xk5FjOpVibRKl2vUpRpIljylBPRCaaY58aB4ErBSPiaNnejB6poDBUA/0?wx_fmt=jpeg","width":null,"height":null},"images":[],"iFrames":[],"videos":[],"contentMd":"\n报价太便宜，中国高铁被踢出保加利亚！\n==================\n\n\n  \n  \n太便宜，中国高铁被踢出保加利亚合同招标了。  \n正常来说，作为招标方的保加利亚当然希望以最低价，修成最好的高铁，这是毋庸置疑的。可为什么保加利亚要把报价最低的中国中车青岛四方公司踢出合同招标呢？**严格来说，不是保加利亚把中车踢了出去，而是欧盟把中车踢了出去。**  \n欧盟的理由是，中国中车拿了巨额补贴，抢欧洲高铁的订单。这个巨额补贴有多高呢？按照欧盟的估算，大约是17.5亿欧元。不过，**这个数字不是单独补贴给保加利亚项目的，而是补贴给中车集团的。**中车集团在海外参与的高铁项目很少，主要是在中国运营。所以，这个补贴不能说，就是专门为了抢保加利亚高铁项目而设立的。  \n从金额上来说，这也是不可能的。整个保加利亚高铁项目总价值才6.1亿欧元，也不需要修高速铁路，只是提供20辆高速列车和为期15年的维修服务、人才培训服务等。欧盟对反补贴的要求是非常宽泛的，不严格的。它只是要求参与竞标的公司，在3年内，从第三方国家获得400万欧元以上的补贴，就需要主动向欧盟汇报自己参与竞标的项目。  \n  \n青岛四方是中车集团旗下的子公司，拿中车集团获得的补贴，来排挤青岛四方子公司，本身就是不公平的。很多人嘲讽说，这事不能怪欧盟，要怪就怪中车的姿态放得太低，竟然以超低价竞标，被踢出去，也是活该。这个说法有没有道理呢？我们来算一笔账。  \n西班牙公司的报价是12.2亿列弗，青岛四方的报价是6.072亿列弗，二者差了一倍的价格。列弗是保加利亚货币，1列弗约等于4人民币，青岛四方差不多就是报价24.288亿元。**这个项目的招标价格是6.1亿欧元，折合人民币是47.56亿，等于青岛四方是以半价竞标。**  \n咱们中国的“和谐”号电力牵引式动车，成本大约在1.5亿元左右。保加利亚要买20辆电力牵引式列车，还要加上15年的后勤维护，人员培训，怎么算，这个价格都在30亿元以上，甚至要达到40亿元，才能回本。  \n  \n说实话，半价竞标，真的很难赚到钱，甚至还可能亏钱。因此，这事不仅欧盟不满意，中国老百姓也很不满意。高铁是高科技产品，怎么能靠超低价竞标呢？如果高科技产品都需要靠超低价竞标，那低技术含量的产品，岂不是要价格内卷到友商都活不下去？**这是不符合市场规律的。**中国人拼命地搞研发，攀登科技树，为的是什么？不是为了把高技术产品卖成白菜价，而是为了让中国产品卖出金子般的价格，也让中国人拿到更高的收入。  \n而且，特别让人不满意的是，西班牙公司的报价是6亿列弗，咱们哪怕报5亿列弗，也行啊。为什么一定要报到3亿列弗？用半价竞标，别人赚不到钱，自己也赚不到钱，何必如此呢？中国的高铁技术为何要贱卖？这种现象不是第一次了。  \n  \n在中国高铁第一次出口土耳其时，就巨亏30个亿，修建沙特麦麦高铁，也亏了40个亿。明知道是亏钱的，为什么中国还要这么做呢？**根本原因就在于，把中国企业扎堆地带进去。高铁只是一个敲门砖，它代表着中国顶尖的基建技术。**  \n跟着高铁一起进去的，还有中国的工程机械、空调设备、桥梁隧道施工等。麦麦高铁没赚钱，但是由于麦麦高铁修得好，沙特几乎所有大型基建项目，都成批地外包给了中国公司。  \n这特别符合中国人的商业逻辑。不管是国内，还是海外，只要是做政企工程，开门第一桩生意可以不赚钱，甚至可以亏点钱，但后面的生意，要把前面亏的钱全部都赚回来。用咱们中国人的话来说，这就叫“人情世故”。  \n  \n而且，在基建出海方面，国企可能是亏钱的，民营企业却都是赚钱的。国内高铁也是这么回事，中国铁路公司一直都是亏钱的，可物流拉起来以后，相关民营企业都是赚钱的。最后，这个亏损也都是以税收的形式，又返回政府了。可现在，欧洲人不适应这套玩法，中国的年轻人也不喜欢这套玩法了。  \n在一个法制越健全，明智越开化的国家，大家都希望是直来直往，公开透明的。做一笔生意，就赚一笔钱，不要动不动就公开算小账，暗地里算大账。现在的很多年轻人都理解不了，但只要是上了年纪的包工头，都非常理解这个门道。  \n**对中国而言，欧亚高铁是“一带一路”中的超级大前提。**从希腊、到保加利亚、到土耳其，还有塞尔维亚，沙特、伊朗、巴基斯坦等，都在这个规划之中。中国真正想要的是，用高铁把整个欧亚大陆全部连接起来，重现丝绸之路，恢复“汉唐盛世”。  \n  \n欧盟排挤中国高铁，是一种贸易保护主义。一方面，欧盟希望自己区域内，统一使用欧盟的高铁技术标准，排挤中国高铁进入。另一方面，也是为了保护欧洲的高铁生意。保加利亚项目是一块敲门砖，这个项目拿下了，整个东欧都会被震撼到。  \n它背后不只是中国高铁会进入，跟着中国高铁一起进入的，还会有中国的空调、电视、机械、汽车等工业制品。  \n我们不要觉得，就欧洲人特别聪明，而中国人特别傻。不过，我们确实需要思考的是，如何将高科技产品卖出高价格？**走廉价路线，不利于共同富裕。**  \n  \n  \n  \n\n\n","contentSummary":{"result":"<title>中国高铁因低价被排除出保加利亚招标</title>\n<description>中国中车青岛四方公司因报价过低被排除出保加利亚高铁项目招标。欧盟认为中国中车因获得巨额补贴而抢占欧洲高铁订单。然而，中国中车的报价实际上是以半价竞标，可能导致亏损。中国高铁的出海策略是以高铁为敲门砖，带动其他中国企业进入海外市场。</description>\n<mindmap>\n- 中国中车青岛四方公司被排除出保加利亚高铁招标\n  - 欧盟认为中国中车获得巨额补贴，抢占欧洲高铁订单\n  - 中国中车以半价竞标，可能导致亏损\n- 中国高铁的出海策略\n  - 高铁作为敲门砖，带动其他中国企业进入海外市场\n  - 中国高铁技术被贱卖，引发争议\n- 欧盟的贸易保护主义\n  - 欧盟希望统一使用欧洲的高铁技术标准，排挤中国高铁\n  - 保护欧洲的高铁生意，防止中国工业制品进入\n</mindmap>\n<comment>高铁的出海策略需要重新审视，过低的报价可能导致亏损，也可能引发其他国家的反感。同时，面对欧盟的贸易保护主义，中国需要寻找更有效的应对策略。</comment>\n<tags>中国, 保加利亚, 贸易护义</tags>","modelType":"gpt-4"},"stat":null}'''
    user_name = "南川"
    user_avatar = 'http://wx.qlogo.cn/mmhead/Q3auHgzwzM7fVxzEwUEk7cYsTVU6ZHWJkUtoh2cPVnREfGS2Igevhg/0'
    
    for i in range(3):
        simulator.run(content, f"{user_name}_{i}", user_avatar)
