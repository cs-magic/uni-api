import re
from enum import Enum
from typing import Optional
from urllib.parse import quote_plus

import pythonmonkey as pm
import requests
from fastapi import APIRouter, Query
from py_mini_racer import MiniRacer

PAGE_KEY = "blogPageUrl"

lofter_router = APIRouter()


class JsEngine(str, Enum):
    py_mini_racer = "py_mini_racer"
    js2py = "js2py"
    pythonmonkey = "pythonmonkey"


class Target(str, Enum):
    es5 = "es5"
    es6 = "es6"


def transform(content: str, engine: JsEngine = JsEngine.pythonmonkey, target: Target = "es5"):
    print("-- replacing")
    if target == "es6":
        content = content.replace("var ", "export var ")

    if target == "es5":
        pattern = r'(var\s+(s\d+)\s*=\s*{};)'

        def replacement(match):
            full_match, var_name = match.groups()
            return f"{full_match}\nexports.{var_name} = {var_name};"

        content = """
exports={}; 
// 在导入任何其他模块之前，首先创建全局的 dwr 对象
dwr = {
  engine: {
    _remoteHandleCallback: function (id, seq, data) {
      // 可以根据需要处理或返回模拟数据
      return;
    },
  },
  // 根据需要添加其他必要的属性和方法
};
        """ + content
        content = re.sub(pattern, replacement, content)
        content += ";\nexports;"

    # print("-- eval content: ", content)
    if engine == JsEngine.py_mini_racer:
        ctx = MiniRacer()
        content = ctx.eval(content)

    elif engine == JsEngine.pythonmonkey:

        content = pm.eval(content, {})

        def replace_null_object(obj):
            if obj is pm.null:
                return None
            elif isinstance(obj, dict):
                return {k: replace_null_object(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_null_object(item) for item in obj]
            else:
                return obj

        content = replace_null_object(content)

    # print("result: ", content)
    items = []
    i = 0
    for key, value in content.items():
        if isinstance(value, dict):
            i += 1
            # print(">> ", i, value)
            # if "blogName" in value:
            if PAGE_KEY in value:
                items.append(value)
    return items


class Category(str, Enum):
    date = "date"
    total = "total"
    week = "week"
    month = "month"


@lofter_router.get("/lofter/search")
async def search_lofter(
    keyword: str = Query(..., description="Search keyword"),
    # 必选参数
    script_session_id: str = Query("${scriptSessionId}187", alias="scriptSessionId", include_in_schema=False),
    http_session_id: Optional[str] = Query(None, alias="httpSessionId", include_in_schema=False),
    script_name: str = Query("TagBean", alias="scriptName", include_in_schema=False),
    method_name: str = Query("search", alias="methodName", include_in_schema=False),
    id: int = Query(0, include_in_schema=False),
    param1: int = Query(0, include_in_schema=False),
    param2: Optional[str] = Query(None, include_in_schema=False),
    category: Category = Query(Category.total),
    param4: bool = Query(False, include_in_schema=False),
    param5: int = Query(0, include_in_schema=False),
    page_size: int = Query(20),
    page_no: int = Query(0),
    param8: int = Query(0, include_in_schema=False),
    batch_id: int = Query(606849, alias="batchId", include_in_schema=False),
    call_count: int = Query(1, alias="callCount", include_in_schema=False)
):
    # 需要转成 %开头 的URL编码
    keyword = quote_plus(keyword)

    # 构造 payload 变量
    payload = f"""callCount={call_count}
scriptSessionId={script_session_id}
httpSessionId={http_session_id or ''}
c0-scriptName={script_name}
c0-methodName={method_name}
c0-id={id}
c0-param0=string:{keyword}
c0-param1=number:{param1}
c0-param2=string:{param2 or ''}
c0-param3=string:{category.value}
c0-param4=boolean:{str(param4).lower()}
c0-param5=number:{param5}
c0-param6=number:{page_size}
c0-param7=number:{page_no}
c0-param8=number:{param8}
batchId={batch_id}"""
    # print(payload)

    url = "https://www.lofter.com/dwr/call/plaincall/TagBean.search.dwr"

    headers = {
        'Referer': 'https://www.lofter.com/tag/puppy/total?tab=archive',
        'Content-Type': 'text/plain',
        'Cookie': 'HMACCOUNT=F2993D5B41121606; Hm_lpvt_c5c55f9c94fbca8efd7d891afb3210e8=1728891466; Hm_lvt_c5c55f9c94fbca8efd7d891afb3210e8=1728891466; JSESSIONID-WLF-XXD=03fb249509f15bfe33d7f12b2df6d0ccf25a6f118b17719982527c11a213eb4de46d76495f2747d89625ed7d53fc85760c7fc277c41590f6b0c190a26f3ffaf66b2aae7b0ea1b88d479ffc6ae2bc97aa86981833227880ca4442ce62694332e1b76438d022512aed218eed17fa4edc0261832f33a10e0c7b9218a474fc3acb51542765be; LOFTER_SESS=Q_yiq1PyLbtcexv_P6dzelQ_pG4j8MSj2pXjVJsa4foL5dmfURVQ8sMe0xOg5aB1Z7j4RinnrzMYAN4PeP7IR-t0EeF672eG5gXnqynPLXpdTzRkVHzE_GzL99DpeIHkkpo_1K3DXeVh4h6FAc4x4hPijmSYSA1wFim0jeR_xMRhi3S4X8f12vDdYHu5YtWFjghLcshT-pj7braVdmmBO9ozWVuH_3on; LOFT_SESSION_ID=AjL0IyRo0rLeXSonKDeaHL5lumQCUm5A; NETEASE_WDA_UID=2216403593#|#1728891481954; firstentry=%2Flogin.do|https%3A%2F%2Fwww.google.com%2F; hb_MA-BFD7-963BF6846668_source=qita297790.lofter.com; reglogin_isLoginFlag=1; regtoken=2000; usertrack=dZPgEWcMyjQ9qd5yA0J5Ag==; NTESwebSI=1E12F50676A469369A03E6A3A08B023A.lofter-webapp-web-old-docker-lftpro-3-3nhsm-87n68-58f9455bdpzrp-8080; __LOFTER_TRACE_UID=E97060C8E14E40F8A11906730F70D22B#2216403593#12; __snaker__id=rBFF6uAyPJBnDDaN; gdxidpyhxdE=Yzs4NhyhMeHhkf5ik%5CIPRcy%5CVRX9%5CSoRRVMWyEf%5Clk9%2FoR4l7SOho40nOXkRdaLJzQ5dSsejJ1qtfCGp7jXDh38SkyewBDBAjSbbz0dsQgAyQp2qRnSMVZt8tgZRjpYUEeKKUx%2FDtjPoZ%2FKEPaXZhRMn1QTIN8VY%5CYhtJ2DvkCIGgdbr%3A1728892367321; noAdvancedBrowser=0'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    content = transform(response.text)
    # print([item[PAGE_KEY] for item in content])
    return content
