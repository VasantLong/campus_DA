# PyECharts iframe 渲染器

用于在 Jupyter Notebook 中通过 iframe 沙箱化渲染 pyecharts 图表，解决 CDN 加载和浏览器追踪防护问题。

## 特性

- ✅ **iframe 沙箱化** - 绕过浏览器 "Tracking Prevention" 限制
- ✅ **CDN 加速** - 使用 bootcdn 快速加载 ECharts
- ✅ **单例模式** - JS 依赖只加载一次，避免重复
- ✅ **灵活配置** - 支持自定义 CDN 和 iframe 尺寸
- ✅ **向后兼容** - 保留原函数调用方式

## 安装

将 `pyecharts_iframe_renderer.py` 放到你的项目目录或 Python 路径中即可使用。

```python
# 方式 1: 直接放在 notebook 同级目录
from pyecharts_iframe_renderer import render_chart, display_chart

# 方式 2: 放到 site-packages
import shutil
shutil.copy('pyecharts_iframe_renderer.py', '/path/to/site-packages/')
```

## 快速开始

```python
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts_iframe_renderer import display_chart

# 创建图表
bar = (
    Bar()
    .add_xaxis(["衬衫", "毛衣", "领带"])
    .add_yaxis("商家A", [114, 55, 27])
    .set_global_opts(title_opts=opts.TitleOpts(title="销售情况"))
)

# 一行代码渲染
display_chart(bar)
```

## API 参考

### 便捷函数

| 函数 | 用途 | 返回值 |
|------|------|--------|
| `render_chart(chart, ...)` | 渲染图表 | HTML 对象 |
| `display_chart(chart, ...)` | 渲染并显示 | None |
| `render_in_iframe(chart, ...)` | 兼容原函数 | HTML 对象 |

### 渲染器类

```python
from pyecharts_iframe_renderer import EChartsRenderer

# 创建渲染器
renderer = EChartsRenderer(cdn_host="https://your-cdn.com/echarts/")

# 渲染图表
html = renderer.render(chart, width="100%", height="500px")
renderer.display(chart)  # 直接显示
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `width` | str | 图表设置或 "100%" | iframe 宽度 |
| `height` | str | 图表设置或 "500px" | iframe 高度 |
| `scrolling` | str | "no" | 滚动设置 |
| `sandbox` | str | "allow-scripts" | 沙箱权限 |
| `cdn_host` | str | bootcdn | ECharts CDN 地址 |

## 高级用法

### 自定义 CDN

```python
from pyecharts_iframe_renderer import EChartsRenderer

renderer = EChartsRenderer(
    cdn_host="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/"
)
renderer.display(chart)
```

### 批量渲染

```python
from pyecharts_iframe_renderer import get_renderer

renderer = get_renderer()  # 单例，JS 只加载一次

for chart in charts:
    renderer.display(chart, height="300px")
```

## 与原代码的区别

| 特性 | 原代码 | 本模块 |
|------|--------|--------|
| 全局变量 | `_echarts_loaded` | 单例模式管理 |
| CDN 配置 | 硬编码 | 可配置 |
| 扩展性 | 固定 | 类结构，易扩展 |
| 复用性 | 复制粘贴 | pip 式导入 |

## 注意事项

1. 必须在 Jupyter 环境中使用（依赖 IPython.display）
2. 确保网络可以访问 CDN 地址
3. 如需离线使用，请下载 echarts.min.js 并修改 CDN 地址为本地路径
