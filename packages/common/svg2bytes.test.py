from packages.common.svg2image import svg_to_bytes, svg_to_image

if __name__ == '__main__':
    s = '''<svg viewBox="0 0 480 640" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="black"/>
  
  <!-- 背景交叉线 -->
  <g stroke="rgba(255,255,255,0.1)" stroke-width="0.5">
    <line x1="0" y1="0" x2="480" y2="640"/>
    <line x1="480" y1="0" x2="0" y2="640"/>
    <line x1="240" y1="0" x2="240" y2="640"/>
    <line x1="0" y1="320" x2="480" y2="320"/>
  </g>
  
  <!-- 环绕圆环 -->
  <g fill="none" stroke="rgba(255,255,255,0.2)">
    <circle cx="240" cy="280" r="180"/>
    <circle cx="240" cy="280" r="150"/>
    <circle cx="240" cy="280" r="120"/>
  </g>
  
  <!-- 中心螺旋 -->
  <path d="M240,280 q-50,50 0,100 t100,0 t0,-100 t-100,0" fill="none" stroke="white" stroke-width="2"/>
  
  <!-- 诗偈文字 -->
  <text x="240" y="460" text-anchor="middle" fill="white" font-size="16" font-family="SimSun, serif">
    <tspan x="240" dy="0">胡族遠征越邊陲，</tspan>
    <tspan x="240" dy="25">博採眾長智慧滋。</tspan>
    <tspan x="240" dy="25">南北融通無界限，</tspan>
    <tspan x="240" dy="25">天人合一道自知。</tspan>
  </text>
  
  <!-- 署名 -->
  <text x="460" y="620" text-anchor="end" fill="rgba(255,255,255,0.5)" font-size="12">@胡博</text>
</svg>'''

    svg_to_image(s, "/Users/mark/coding/codebase-py/apps/uni-api/.out/test.png")
