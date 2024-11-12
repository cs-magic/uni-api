import re
import os
from typing import List
import cairosvg
from pathlib import Path
import platform
from PIL import Image
from io import BytesIO

def get_system_chinese_font() -> str:
    """获取系统可用的中文字体"""
    system = platform.system()
    fonts = {
        "Darwin": ["PingFang SC", "Hiragino Sans GB", "STHeiti"],
        "Windows": ["Microsoft YaHei", "SimHei", "SimSun"],
    }.get(system, [])
    
    fonts.append("sans-serif")
    return f'font-family="{", ".join(fonts)}"'

def extract_svgs(text: str) -> List[str]:
    """从文本中提取所有的 SVG 代码"""
    return re.findall(r'<svg[\s\S]*?</svg>', text)

def ensure_chinese_fonts(svg_content: str) -> str:
    """确保SVG中的文本元素都有合适的中文字体设置"""
    system = platform.system()
    
    # 根据操作系统选择合适的中文字体
    if system == "Darwin":  # macOS
        chinese_fonts = ['PingFang SC', 'Hiragino Sans GB', 'STHeiti', 'Apple LiSung']
    elif system == "Windows":
        chinese_fonts = ['Microsoft YaHei', 'SimSun', 'NSimSun', 'SimHei', 'KaiTi']
    else:  # Linux 和其他系统
        # # 安装文泉驿字体
        # sudo apt-get install ttf-wqy-microhei ttf-wqy-zenhei
        # 安装思源字体
        # sudo apt-get install fonts-noto-cjk fonts-noto-cjk-extra
        # 安装其他中文字体
        # sudo apt-get install fonts-arphic-uming fonts-arphic-ukai
        chinese_fonts = [
            # 思源字体
            'Noto Sans CJK SC', 'Noto Sans SC', 'Noto Serif CJK SC', 'Noto Serif SC',
            # 文泉驿字体
            'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'WenQuanYi Zen Hei Sharp',
            # 其他常用中文字体
            'Source Han Sans CN', 'Source Han Serif CN',
            'AR PL UMing CN', 'AR PL KaitiM GB', 'DroidSansFallback',
            # Ubuntu 自带中文字体
            'Ubuntu', 'Liberation Sans'
        ]
    
    # 添加通用后备字体
    chinese_fonts.extend(['sans-serif', 'serif'])
    
    # 查找所有text元素
    pattern = r'<text([^>]*)>'
    
    def add_font_family(match):
        attrs = match.group(1)
        # 移除已存在的font-family属性（如果有的话）
        attrs = re.sub(r'\s*font-family="[^"]*"', '', attrs)
        # 添加新的font-family属性
        font_str = f' font-family="{", ".join(chinese_fonts)}"'
        return f'<text{attrs}{font_str}>'
    
    # 替换所有匹配项
    processed_svg = re.sub(pattern, add_font_family, svg_content)
    return processed_svg

def svg_to_image(
    svg_content: str,
    output_path: str,
    ppi: int = 300,
    format: str = 'png'
) -> Path:
    """将 SVG 转换为图像文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 预处理SVG确保中文字体支持
    processed_svg = ensure_chinese_fonts(svg_content)
    
    scale = ppi / 96.0
    
    # 使用 UTF-8 编码
    svg_bytes = processed_svg.encode('utf-8')
    
    # PDF 格式需要特殊处理以避免内存问题
    if format.lower() == 'pdf':
        temp_png = output_path + '.temp.png'
        try:
            cairosvg.svg2png(
                bytestring=svg_bytes,
                write_to=temp_png,
                scale=scale * 2,
                dpi=ppi * 2
            )
            Image.open(temp_png).convert('RGB').save(output_path, 'PDF', resolution=ppi)
            os.remove(temp_png)
        except Exception as e:
            if os.path.exists(temp_png):
                os.remove(temp_png)
            raise e
    else:
        convert_method = {'png': cairosvg.svg2png, 'ps': cairosvg.svg2ps}.get(format.lower())
        if not convert_method:
            raise ValueError(f"Unsupported format: {format}")
        
        convert_method(
            bytestring=svg_bytes,
            write_to=output_path,
            scale=scale,
            dpi=ppi
        )
    
    return Path(output_path)

def svg_to_bytes(
    svg_content: str,
    ppi: int = 300,
    format: str = 'png'
) -> BytesIO:
    """将 SVG 转换为字节流，用于 FastAPI 响应
    
    Args:
        svg_content: SVG 内容
        ppi: 图像分辨率
        format: 输出格式 ('png', 'pdf', 'ps')
    
    Returns:
        BytesIO: 包含图像数据的字节流
    """
    # 预处理SVG确保中文字体支持
    processed_svg = ensure_chinese_fonts(svg_content)
    
    scale = ppi / 96.0
    output = BytesIO()
    
    # PDF 格式需要特殊处理以避免内存问题
    if format.lower() == 'pdf':
        temp_buffer = BytesIO()
        try:
            cairosvg.svg2png(
                bytestring=processed_svg.encode('utf-8'),
                write_to=temp_buffer,
                scale=scale * 2,
                dpi=ppi * 2
            )
            temp_buffer.seek(0)
            Image.open(temp_buffer).convert('RGB').save(output, 'PDF', resolution=ppi)
        finally:
            temp_buffer.close()
    else:
        convert_method = {'png': cairosvg.svg2png, 'ps': cairosvg.svg2ps}.get(format.lower())
        if not convert_method:
            raise ValueError(f"Unsupported format: {format}")
        
        convert_method(
            bytestring=processed_svg.encode('utf-8'),
            write_to=output,
            scale=scale,
            dpi=ppi
        )
    
    output.seek(0)
    return output

if __name__ == "__main__":
    sample_text = '''作为一位得道高僧，我将为穆冠群生成一首独特的、富有禅意和哲理的诗偈：

步骤：
1. 解析姓名：穆意为安静、和谐；冠群意为冠绝群伦。
2. 联想意境：高山流水，群峰中的主峰。
3. 融入禅意：静中见动，动中求静。
4. 构思诗句：四句七言，押韵。

诗偈：

穆然群峰立苍穹，
冠绝一峰显奇峥。
静观浮华皆幻影，
群动不惊道自通。

接下来，我将基于这首诗偈和穆冠群的名字，为他创作一个独特的人生图腾：

步骤：
1. 选择核心图形：山峰，象征"冠群"之意。
2. 融入诗意：用线条表现静中有动。
3. 体现禅意：简约线条，留白。
4. 加入个人特色：将"穆"字的部首"艹"融入设计。

现在，我将使用SVG代码来呈现这个设计：

<svg viewBox="0 0 480 640" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="black"/>
  
  <!-- 主要图形：山峰 -->
  <path d="M240,100 L140,400 L340,400 Z" fill="none" stroke="white" stroke-width="2"/>
  
  <!-- 融入"艹"部首 -->
  <path d="M220,80 L260,80 M240,60 L240,100" stroke="white" stroke-width="1.5"/>
  
  <!-- 动态线条 -->
  <path d="M140,400 Q240,250 340,400" fill="none" stroke="white" stroke-width="1" opacity="0.6"/>
  
  <!-- 诗偈 -->
  <text x="240" y="460" font-family="SimSun, serif" font-size="16" fill="white" text-anchor="middle">
    <tspan x="240" dy="0">穆然群峰立蒼穹</tspan>
    <tspan x="240" dy="24">冠絕一峰顯奇峥</tspan>
    <tspan x="240" dy="24">靜觀浮華皆幻影</tspan>
    <tspan x="240" dy="24">群動不驚道自通</tspan>
  </text>
  
  <!-- 署名 -->
  <text x="460" y="620" font-family="SimSun, serif" font-size="12" fill="white" text-anchor="end">@穆冠群</text>
</svg>'''

    if svgs := extract_svgs(sample_text):
        output_dir = ".out"
        os.makedirs(output_dir, exist_ok=True)
        
        for fmt, ppis in [('png', [72, 300]), ('pdf', [72, 300])]:
            for ppi in ppis:
                output_path = os.path.join(output_dir, f"totem_{ppi}ppi.{fmt}")
                try:
                    output_file = svg_to_image(svgs[0], output_path, ppi, fmt)
                    print(f"Successfully created {output_file} with {ppi} PPI")
                except Exception as e:
                    print(f"Error creating {output_path}: {str(e)}")
    else:
        print("No SVG found in the sample text")

