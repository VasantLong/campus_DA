# PyECharts Jupyter Exporter 使用文档

> **版本**: 1.0.0  
> **更新日期**: 2026-03-31  
> **默认 CDN**: jsDelivr GitHub 加速 (`https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/`)

---

## 📋 目录

1. [概述](#概述)
2. [安装与导入](#安装与导入)
3. [快速开始](#快速开始)
4. [API 参考](#api-参考)
   - [常量](#常量)
   - [类](#类)
   - [函数](#函数)
5. [使用场景](#使用场景)
6. [CDN 配置指南](#cdn-配置指南)
7. [常见问题](#常见问题)
8. [最佳实践](#最佳实践)

---

## 概述

`pyecharts_jupyter_exporter` 是一个统一的 PyECharts Jupyter Notebook 导出模块，整合了以下功能：

- **iframe 沙箱化渲染**: 解决 Jupyter 中 CDN 加载和浏览器追踪防护问题
- **CDN 统一管理**: 默认使用 jsDelivr GitHub 加速，支持多 CDN 切换
- **动态依赖分析**: 自动分析图表所需的 JS 依赖并生成对应 CDN URL
- **便捷导出**: 一键生成可嵌入的 HTML 代码

---

## 安装与导入

### 文件放置

将 `pyecharts_jupyter_exporter.py` 放置在项目目录或 Python 路径中：

```
project/
├── pyecharts_jupyter_exporter.py  # 本模块
├── notebook.ipynb                 # Jupyter Notebook
└── ...
```

### 导入方式

```python
# 方式 1: 导入全部
import pyecharts_jupyter_exporter as pje

# 方式 2: 按需导入
from pyecharts_jupyter_exporter import (
    display_chart,           # 快速显示图表
    render_chart,            # 渲染为 HTML 对象
    get_chart_dependencies,  # 获取依赖信息
    JSDELIVR_GH_BASE,        # CDN 基础地址常量
    CDN_CONFIGS,             # CDN 配置字典
    RESOURCE_URLS,           # 常用资源链接
)
```

---

## 快速开始

### 1. 基础图表显示

```python
from pyecharts.charts import Bar
from pyecharts_jupyter_exporter import display_chart

# 创建图表
bar = Bar()
bar.add_xaxis(["A", "B", "C", "D", "E"])
bar.add_yaxis("Series 1", [5, 20, 36, 10, 75])

# 在 Jupyter 中显示（自动使用 iframe 沙箱）
display_chart(bar, width="100%", height="500px")
```

### 2. 查看 CDN 依赖

```python
from pyecharts_jupyter_exporter import get_chart_dependencies

info = get_chart_dependencies(bar)
print(info["dependencies"])  # ['echarts']
print(info["cdn_urls"])      # ['https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/echarts.min.js']
```

---

## API 参考

### 常量

#### `JSDELIVR_GH_BASE`

**类型**: `str`  
**默认值**: `https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/`  
**说明**: jsDelivr GitHub 加速 CDN 的基础地址

```python
from pyecharts_jupyter_exporter import JSDELIVR_GH_BASE
print(JSDELIVR_GH_BASE)
# 输出: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/
```

#### `DEFAULT_CDN`

**类型**: `str`  
**默认值**: `"jsdelivr_gh"`  
**说明**: 默认 CDN 提供商名称

#### `CDN_CONFIGS`

**类型**: `Dict[str, str]`  
**说明**: 可用的 CDN 配置字典

| 键名          | 说明                          | 地址                                                                    |
| ------------- | ----------------------------- | ----------------------------------------------------------------------- |
| `jsdelivr_gh` | **默认** jsDelivr GitHub 加速 | `https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/` |
| `bootcdn`     | BootCDN                       | `https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/`                      |
| `pyecharts`   | PyECharts 官方                | `https://assets.pyecharts.org/assets/v6/`                               |
| `staticfile`  | Staticfile                    | `https://cdn.staticfile.org/echarts/5.4.3/`                             |
| `jsdelivr`    | jsDelivr NPM                  | `https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/`                      |
| `kesci`       | Kesci                         | `https://cdn.kesci.com/lib/pyecharts_assets/`                           |

```python
from pyecharts_jupyter_exporter import CDN_CONFIGS

# 查看所有可用 CDN
for name, url in CDN_CONFIGS.items():
    print(f"{name}: {url}")

# 使用特定 CDN 渲染
display_chart(bar, cdn_provider="bootcdn")
```

#### `RESOURCE_URLS`

**类型**: `Dict[str, str]`  
**说明**: 常用资源的直接访问链接

**核心库**:

- `echarts`: ECharts 核心库

**扩展插件**:

- `echarts-gl`: 3D 图表支持
- `echarts-wordcloud`: 词云图
- `echarts-liquidfill`: 水球图
- `echarts-stat`: 统计扩展

**地图数据**:

- `china`: 中国地图
- `world`: 世界地图
- `china-cities`: 中国城市地图

**主题**:

- `theme-dark`: 暗黑主题
- `theme-macarons`: 马卡龙主题
- `theme-vintage`: 复古主题
- `theme-shine`: 闪亮主题

```python
from pyecharts_jupyter_exporter import RESOURCE_URLS

# 获取中国地图 CDN 链接
china_url = RESOURCE_URLS["china"]
print(china_url)
# 输出: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/maps/china
```

---

### 类

#### `JSDependencyManager`

**说明**: JS 依赖管理器，负责分析图表所需的 JS 依赖并生成 CDN URL

**初始化**:

```python
manager = JSDependencyManager(
    cdn_provider: str = "jsdelivr_gh",  # CDN 提供商
    custom_cdn_base: str = None         # 自定义 CDN 基础 URL
)
```

**方法**:

##### `get_url(dep: str) -> str`

获取单个依赖的 CDN URL

```python
manager = JSDependencyManager()
url = manager.get_url("echarts")
print(url)
# 输出: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/echarts.min.js
```

##### `get_dependencies(chart: Base) -> Dict`

获取图表的所有依赖信息

**返回字典结构**:

```python
{
    "dependencies": ["echarts", "china"],  # 依赖名称列表
    "cdn_urls": ["https://...", "https://..."],  # CDN URL 列表
    "html_tags": "<script src=...></script>\n<script src=...></script>",  # HTML 标签
    "cdn_provider": "jsdelivr_gh",  # CDN 提供商
    "cdn_base": "https://..."  # CDN 基础地址
}
```

```python
from pyecharts.charts import Map

map_chart = Map()
map_chart.add("", [("广东", 100)], "china")

manager = JSDependencyManager()
info = manager.get_dependencies(map_chart)

print(info["dependencies"])  # ['echarts', 'china']
print(info["cdn_urls"])
# ['https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/echarts.min.js',
#  'https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/maps/china.js']
```

##### `get_loader_script(chart: Base) -> str`

获取动态加载 JS 的 JavaScript 代码（Promise 链式加载）

```python
script = manager.get_loader_script(chart)
# 返回可直接插入 HTML 的 <script> 标签代码
```

---

#### `EChartsRenderer`

**说明**: PyECharts iframe 渲染器，单例模式

**初始化**:

```python
renderer = EChartsRenderer(
    cdn_provider: str = "jsdelivr_gh",  # CDN 提供商
    custom_cdn_base: str = None         # 自定义 CDN 基础 URL
)
```

**方法**:

##### `render(chart: Base, width=None, height=None, scrolling="no", sandbox="allow-scripts", force_reload=False) -> HTML`

在 iframe 中渲染图表

**参数**:

- `chart`: PyECharts 图表实例
- `width`: iframe 宽度（默认从图表获取或 "100%"）
- `height`: iframe 高度（默认从图表获取或 "500px"）
- `scrolling`: 滚动设置（默认 "no"）
- `sandbox`: 沙箱权限（默认 "allow-scripts"）
- `force_reload`: 强制重新加载依赖（默认 False）

**返回**: `IPython.display.HTML` 对象

```python
from pyecharts_jupyter_exporter import EChartsRenderer
from pyecharts.charts import Line

line = Line()
line.add_xaxis(["Mon", "Tue", "Wed"])
line.add_yaxis("Sales", [120, 200, 150])

renderer = EChartsRenderer()
html_obj = renderer.render(line, width="800px", height="400px")
display(html_obj)
```

##### `display(chart: Base, **kwargs)`

直接显示图表（便捷方法）

```python
renderer = EChartsRenderer()
renderer.display(line, width="100%", height="500px")
```

##### `get_dependencies_info(chart: Base) -> Dict`

获取图表依赖信息（用于调试）

```python
info = renderer.get_dependencies_info(line)
print(info)
```

---

### 函数

#### `get_renderer(cdn_provider=DEFAULT_CDN, custom_cdn_base=None) -> EChartsRenderer`

获取或创建 EChartsRenderer 实例（单例）

```python
from pyecharts_jupyter_exporter import get_renderer

renderer = get_renderer()
# 或指定 CDN
renderer = get_renderer(cdn_provider="bootcdn")
```

---

#### `render_chart(chart, width=None, height=None, cdn_provider=DEFAULT_CDN, custom_cdn_base=None, **kwargs) -> HTML`

快速渲染图表到 iframe（最常用函数）

```python
from pyecharts_jupyter_exporter import render_chart

# 基础用法
html = render_chart(bar)

# 指定尺寸
html = render_chart(bar, width="800px", height="600px")

# 切换 CDN
html = render_chart(bar, cdn_provider="pyecharts")

# 自定义 CDN
html = render_chart(bar, custom_cdn_base="https://my-cdn.com/assets/")
```

---

#### `display_chart(chart, **kwargs)`

快速显示图表（最便捷函数）

```python
from pyecharts_jupyter_exporter import display_chart

# 一行代码显示图表
display_chart(bar)

# 指定参数
display_chart(bar, width="100%", height="500px", cdn_provider="bootcdn")
```

---

#### `get_chart_dependencies(chart, cdn_provider=DEFAULT_CDN) -> Dict`

获取图表所需的 JS 依赖信息

```python
from pyecharts_jupyter_exporter import get_chart_dependencies

info = get_chart_dependencies(bar)
print(f"依赖: {info['dependencies']}")
print(f"CDN URLs: {info['cdn_urls']}")
print(f"HTML 标签: {info['html_tags']}")
```

---

#### `get_jsdelivr_gh_url(dep: str) -> str`

获取 jsDelivr GitHub 加速 CDN URL（兼容函数）

```python
from pyecharts_jupyter_exporter import get_jsdelivr_gh_url

url = get_jsdelivr_gh_url("echarts-gl")
print(url)
# 输出: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/echarts-gl.min.js
```

---

#### `get_chart_cdn_urls(chart: Chart) -> Dict`

获取图表的所有 CDN URL（兼容函数）

```python
from pyecharts_jupyter_exporter import get_chart_cdn_urls

info = get_chart_cdn_urls(bar)
print(info["urls"])
print(info["html_tags"])
```

---

#### `print_chart_cdn_info(chart: Chart, chart_name: str = "Chart")`

打印图表的 CDN 信息（调试工具）

```python
from pyecharts_jupyter_exporter import print_chart_cdn_info

print_chart_cdn_info(bar, "我的柱状图")
# 输出:
# 📊 我的柱状图
# --------------------------------------------------------------------------------
# 基础地址: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/
# 依赖: ['echarts']
# CDN 链接:
#   - echarts: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/echarts.min.js
```

---

## 使用场景

### 场景 1: Jupyter Notebook 中显示图表

```python
from pyecharts.charts import Pie
from pyecharts_jupyter_exporter import display_chart

pie = Pie()
pie.add("", [("A", 30), ("B", 70)])

# 直接显示
display_chart(pie, width="600px", height="400px")
```

### 场景 2: 使用地图数据

```python
from pyecharts.charts import Map
from pyecharts_jupyter_exporter import display_chart

map_chart = Map()
map_chart.add(
    "销售额",
    [("广东", 100), ("北京", 80), ("上海", 90)],
    "china"
)

# 自动加载 echarts + china 地图依赖
display_chart(map_chart)
```

### 场景 3: 3D 图表

```python
from pyecharts.charts import Bar3D
from pyecharts_jupyter_exporter import display_chart

bar3d = Bar3D()
data = [[0, 0, 5], [1, 1, 10], [2, 2, 15]]
bar3d.add("", data)

# 自动加载 echarts-gl 扩展
display_chart(bar3d, width="800px", height="600px")
```

### 场景 4: 词云图

```python
from pyecharts.charts import WordCloud
from pyecharts_jupyter_exporter import display_chart

words = [("Python", 100), ("Data", 80), ("AI", 90)]
wordcloud = WordCloud()
wordcloud.add("", words)

# 自动加载 echarts-wordcloud 扩展
display_chart(wordcloud)
```

### 场景 5: 导出独立 HTML 文件

```python
from pyecharts_jupyter_exporter import render_chart

html_obj = render_chart(bar)

# 保存到文件
with open("chart.html", "w", encoding="utf-8") as f:
    f.write(html_obj.data)
```

### 场景 6: 批量生成报告

```python
from pyecharts_jupyter_exporter import display_chart, CDN_CONFIGS

charts = [bar1, bar2, line1, pie1]

for i, chart in enumerate(charts):
    print(f"图表 {i+1}:")
    display_chart(chart, width="100%", height="400px")
```

---

## CDN 配置指南

### 切换 CDN 提供商

```python
from pyecharts_jupyter_exporter import display_chart

# 方式 1: 使用预配置 CDN
display_chart(bar, cdn_provider="bootcdn")
display_chart(bar, cdn_provider="pyecharts")

# 方式 2: 使用自定义 CDN
display_chart(bar, custom_cdn_base="https://cdn.example.com/pyecharts/")
```

### 自定义 CDN 格式要求

自定义 CDN 需要遵循 pyecharts-assets 的目录结构：

```
https://your-cdn.com/assets/
├── echarts.min.js
├── echarts-gl.min.js
├── echarts-wordcloud.min.js
├── maps/
│   ├── china.js
│   └── world.js
└── themes/
    ├── dark.js
    └── macarons.js
```

### CDN 选择建议

| 场景       | 推荐 CDN                  | 说明                     |
| ---------- | ------------------------- | ------------------------ |
| 国内访问   | `bootcdn` / `jsdelivr_gh` | 国内速度快               |
| 海外访问   | `jsdelivr` / `pyecharts`  | 全球加速                 |
| 内网环境   | `custom`                  | 私有 CDN                 |
| 稳定性优先 | `jsdelivr_gh`             | GitHub + jsDelivr 双加速 |

---

## 常见问题

### Q1: 图表显示空白？

**可能原因**:

1. CDN 加载失败
2. 依赖未正确加载

**解决方案**:

```python
# 检查依赖
from pyecharts_jupyter_exporter import get_chart_dependencies

info = get_chart_dependencies(chart)
print(info["cdn_urls"])  # 检查 CDN 链接是否可访问

# 尝试切换 CDN
display_chart(chart, cdn_provider="bootcdn")
```

### Q2: 地图数据加载失败？

**解决方案**:

```python
from pyecharts_jupyter_exporter import RESOURCE_URLS

# 检查地图资源链接
print(RESOURCE_URLS["china"])

# 确保使用正确的地图名称
map_chart.add("", data, "china")  # 使用 "china" 而不是 "中国"
```

### Q3: 如何离线使用？

**解决方案**:

1. 下载 pyecharts-assets: https://github.com/pyecharts/pyecharts-assets
2. 启动本地服务器: `python -m http.server 8000`
3. 使用自定义 CDN:

```python
display_chart(chart, custom_cdn_base="http://localhost:8000/assets/")
```

### Q4: iframe 高度自适应？

**解决方案**:

```python
# 手动设置高度
display_chart(chart, height="600px")

# 或根据内容调整（需要图表支持）
chart.height = "600px"
display_chart(chart)
```

### Q5: 多个图表 CDN 重复加载？

**解决方案**: 使用单例渲染器

```python
from pyecharts_jupyter_exporter import get_renderer

renderer = get_renderer()

# 同一渲染器会自动缓存已加载的依赖
renderer.display(chart1)
renderer.display(chart2)  # 共享已加载的 echarts
```

---

## 最佳实践

### 1. 项目初始化配置

```python
# 在 notebook 开头统一配置
from pyecharts_jupyter_exporter import set_jsdelivr_gh_cdn, CDN_CONFIGS
from pyecharts.globals import CurrentConfig

# 设置全局 CDN
# 或根据网络环境选择
# CDN_CONFIGS.keys() 查看所有选项
```

### 2. 统一图表样式

```python
from pyecharts import options as opts
from pyecharts.globals import ThemeType

def create_chart(title, chart_type="bar"):
    """统一图表创建函数"""
    if chart_type == "bar":
        from pyecharts.charts import Bar
        chart = Bar(init_opts=opts.InitOpts(
            theme=ThemeType.MACARONS,
            width="100%",
            height="500px"
        ))
    # ... 其他类型
    chart.set_global_opts(title_opts=opts.TitleOpts(title=title))
    return chart

# 使用
bar = create_chart("销售数据")
bar.add_xaxis([...])
bar.add_yaxis(...)
display_chart(bar)
```

### 3. 批量导出 HTML

```python
from pyecharts_jupyter_exporter import render_chart

def export_charts(charts_dict, output_dir="./exports"):
    """批量导出图表为 HTML 文件"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    for name, chart in charts_dict.items():
        html_obj = render_chart(chart)
        filepath = os.path.join(output_dir, f"{name}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_obj.data)
        print(f"已导出: {filepath}")

# 使用
charts = {
    "sales": bar_chart,
    "trends": line_chart,
    "distribution": pie_chart
}
export_charts(charts)
```

### 4. 调试模式

```python
from pyecharts_jupyter_exporter import print_chart_cdn_info, get_chart_dependencies

def debug_chart(chart, name="Chart"):
    """调试图表配置"""
    print_chart_cdn_info(chart, name)

    info = get_chart_dependencies(chart)
    print("\n依赖详情:")
    for dep, url in zip(info["dependencies"], info["cdn_urls"]):
        print(f"  {dep}: {url}")

    # 检查链接可访问性（可选）
    import requests
    print("\n链接检查:")
    for url in info["cdn_urls"]:
        try:
            resp = requests.head(url, timeout=5)
            status = "✅" if resp.status_code == 200 else f"❌ {resp.status_code}"
        except Exception as e:
            status = f"❌ {str(e)[:30]}"
        print(f"  {status}: {url[:60]}...")

# 使用
debug_chart(complex_chart, "复杂图表")
```

### 5. 网络异常处理

```python
from pyecharts_jupyter_exporter import display_chart, CDN_CONFIGS

def safe_display(chart, preferred_cdns=None):
    """带故障转移的图表显示"""
    preferred_cdns = preferred_cdns or ["jsdelivr_gh", "bootcdn", "pyecharts"]

    for cdn in preferred_cdns:
        try:
            display_chart(chart, cdn_provider=cdn)
            print(f"✅ 使用 CDN: {cdn}")
            return
        except Exception as e:
            print(f"❌ CDN {cdn} 失败: {e}")

    print("所有 CDN 均失败，请检查网络连接")

# 使用
safe_display(chart)
```

---

## 版本历史

| 版本  | 日期       | 更新内容                              |
| ----- | ---------- | ------------------------------------- |
| 1.0.0 | 2026-03-31 | 初始版本，整合 iframe 渲染和 CDN 管理 |

---

## 相关链接

- **PyECharts 官方文档**: https://pyecharts.org/
- **pyecharts-assets**: https://github.com/pyecharts/pyecharts-assets
- **jsDelivr**: https://www.jsdelivr.com/
- **BootCDN**: https://www.bootcdn.cn/

---

**文档结束**

如有问题，请检查：

1. 网络连接是否正常
2. CDN 链接是否可访问
3. pyecharts 版本是否兼容（建议 v2.0+）
