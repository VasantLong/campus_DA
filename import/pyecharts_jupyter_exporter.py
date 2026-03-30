#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyECharts Jupyter HTML 导出模块

功能：
1. iframe 沙箱化渲染 pyecharts 图表
2. 统一管理 CDN 资源（默认使用 jsDelivr GitHub 加速）
3. 支持动态 JS 依赖分析和加载
4. 提供便捷的 HTML 导出功能

默认 CDN: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/
"""

from IPython.display import display, HTML
import html
from typing import Dict, List, Optional, Union

from pyecharts.globals import CurrentConfig, NotebookType
from pyecharts.charts.base import Base
from pyecharts.charts.chart import Chart
from pyecharts.datasets import FILENAMES

# 配置 Notebook 类型
CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_NOTEBOOK


# ========== CDN 配置（统一使用 jsDelivr GitHub 加速）==========

# jsDelivr GitHub 加速基础地址（默认）
JSDELIVR_GH_BASE = "https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/"

# 备用 CDN 配置（可选切换）
CDN_CONFIGS = {
    "jsdelivr_gh": JSDELIVR_GH_BASE,  # 默认：jsDelivr GitHub 加速
    "bootcdn": "https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/",
    "pyecharts": "https://assets.pyecharts.org/assets/v6/",
    "staticfile": "https://cdn.staticfile.org/echarts/5.4.3/",
    "jsdelivr": "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/",
    "kesci": "https://cdn.kesci.com/lib/pyecharts_assets/",
}

DEFAULT_CDN = "jsdelivr_gh"


# ========== 常用资源快速访问链接 ==========

RESOURCE_URLS = {
    # 核心库
    "echarts": f"{JSDELIVR_GH_BASE}echarts.min",

    # 扩展插件
    "echarts-gl": f"{JSDELIVR_GH_BASE}echarts-gl.min",
    "echarts-wordcloud": f"{JSDELIVR_GH_BASE}echarts-wordcloud.min",
    "echarts-liquidfill": f"{JSDELIVR_GH_BASE}echarts-liquidfill.min",
    "echarts-stat": f"{JSDELIVR_GH_BASE}ecStat.min",

    # 地图数据
    "china": f"{JSDELIVR_GH_BASE}maps/china",
    "world": f"{JSDELIVR_GH_BASE}maps/world",
    "china-cities": f"{JSDELIVR_GH_BASE}maps/china-cities",

    # 主题
    "theme-dark": f"{JSDELIVR_GH_BASE}themes/dark",
    "theme-macarons": f"{JSDELIVR_GH_BASE}themes/macarons",
    "theme-vintage": f"{JSDELIVR_GH_BASE}themes/vintage",
    "theme-shine": f"{JSDELIVR_GH_BASE}themes/shine",
}


# ========== JS 依赖管理器 ==========

class JSDependencyManager:
    """
    JS 依赖管理器

    负责分析图表所需的 JS 依赖并生成对应的 CDN URL 和 HTML 标签。
    默认使用 jsDelivr GitHub 加速 CDN。
    """

    def __init__(self, cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None):
        """
        初始化依赖管理器

        Args:
            cdn_provider: CDN 提供商名称 ("jsdelivr_gh", "bootcdn", "pyecharts", ...)
            custom_cdn_base: 自定义 CDN 基础 URL（优先级最高）
        """
        if custom_cdn_base:
            self.cdn_base = custom_cdn_base
            self.provider = "custom"
        elif cdn_provider in CDN_CONFIGS:
            self.cdn_base = CDN_CONFIGS[cdn_provider]
            self.provider = cdn_provider
        else:
            raise ValueError(f"不支持的 CDN 提供商: {cdn_provider}")

    def get_url(self, dep: str) -> str:
        """
        获取单个依赖的 CDN URL（兼容 pyecharts_jsdelivr_gh.py 的接口）

        Args:
            dep: 依赖名称 (echarts, china, echarts-gl, 等)

        Returns:
            完整的 CDN URL
        """
        return self._build_url(dep)

    def get_dependencies(self, chart: Base) -> Dict:
        """
        获取图表所需的 JS 依赖信息

        Returns:
            {
                "dependencies": ["echarts", "china", ...],
                "cdn_urls": ["https://...", ...],
                "html_tags": "<script...>\n<script...>",
                "cdn_provider": "jsdelivr_gh",
                "cdn_base": "https://..."
            }
        """
        # 获取依赖列表（去重）
        deps = list(dict.fromkeys(chart.js_dependencies.items))

        # 生成 CDN URL
        urls = [self._build_url(dep) for dep in deps]

        # 生成 HTML script 标签
        html_tags = "\n".join([f'<script src="{url}"></script>' for url in urls])

        return {
            "dependencies": deps,
            "cdn_urls": urls,
            "html_tags": html_tags,
            "cdn_provider": self.provider,
            "cdn_base": self.cdn_base
        }

    def _build_url(self, dep: str) -> str:
        """构建单个依赖的 CDN URL"""
        if dep in FILENAMES:
            filename, ext = FILENAMES[dep]
            file_fullname = f"{filename}.{ext}"
        else:
            file_fullname = f"{dep}.js"

        # 特殊处理不同 CDN 的路径格式
        if self.provider in ["pyecharts", "kesci", "jsdelivr_gh"]:
            # 这些 CDN 使用 pyecharts-assets 的标准路径格式
            url = f"{self.cdn_base}{file_fullname}"
        else:
            # 其他 CDN（如 bootcdn, staticfile）使用不同的路径格式
            if dep == "echarts":
                url = f"{self.cdn_base}echarts.min.js"
            else:
                url = f"{self.cdn_base}{file_fullname}"

        return url

    def get_loader_script(self, chart: Base) -> str:
        """
        获取动态加载 JS 的脚本（Promise 链式加载）

        Returns:
            JavaScript 代码字符串
        """
        dep_info = self.get_dependencies(chart)
        urls = dep_info["cdn_urls"]
        urls_json = str(urls).replace("'", '"')

        return f"""
        <script>
        (function() {{
            var urls = {urls_json};

            function loadScript(url) {{
                return new Promise(function(resolve, reject) {{
                    if (window.__loaded_scripts && window.__loaded_scripts[url]) {{
                        resolve();
                        return;
                    }}
                    var script = document.createElement('script');
                    script.src = url;
                    script.onload = function() {{
                        if (!window.__loaded_scripts) window.__loaded_scripts = {{}};
                        window.__loaded_scripts[url] = true;
                        resolve();
                    }};
                    script.onerror = reject;
                    document.head.appendChild(script);
                }});
            }}

            urls.reduce(function(chain, url) {{
                return chain.then(function() {{ return loadScript(url); }});
            }}, Promise.resolve());
        }})();
        </script>
        """.strip()


# ========== iframe 渲染器 ==========

class EChartsRenderer:
    """
    PyECharts iframe 渲染器（支持动态依赖，默认 jsDelivr GitHub 加速）
    """

    _instance = None
    _loaded_dependency_sets: set = set()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None):
        if hasattr(self, '_initialized'):
            return
        self.dep_manager = JSDependencyManager(cdn_provider, custom_cdn_base)
        self._initialized = True

    def _ensure_dependencies_loaded(self, chart: Base, force_reload: bool = False):
        """确保图表所需的 JS 依赖已加载"""
        dep_info = self.dep_manager.get_dependencies(chart)
        deps_tuple = tuple(dep_info["dependencies"])

        if not force_reload and deps_tuple in EChartsRenderer._loaded_dependency_sets:
            return

        script = self.dep_manager.get_loader_script(chart)
        display(HTML(script))
        EChartsRenderer._loaded_dependency_sets.add(deps_tuple)

    def render(self, chart: Base, width: str = None, height: str = None,
               scrolling: str = "no", sandbox: str = "allow-scripts",
               force_reload: bool = False) -> HTML:
        """
        在 iframe 中渲染 pyecharts 图表

        Args:
            chart: pyecharts 图表实例
            width: iframe 宽度
            height: iframe 高度
            scrolling: 滚动设置
            sandbox: 沙箱权限
            force_reload: 是否强制重新加载依赖

        Returns:
            IPython.display.HTML 对象
        """
        self._ensure_dependencies_loaded(chart, force_reload)

        html_content = chart.render_embed()
        escaped_html = html.escape(html_content)

        iframe_width = width or getattr(chart, 'width', '100%')
        iframe_height = height or getattr(chart, 'height', '500px')

        iframe_html = f"""
        <iframe srcdoc="{escaped_html}" 
                width="{iframe_width}" 
                height="{iframe_height}" 
                frameborder="0"
                scrolling="{scrolling}"
                sandbox="{sandbox}">
        </iframe>
        """
        return HTML(iframe_html)

    def display(self, chart: Base, **kwargs):
        """直接显示图表"""
        display(self.render(chart, **kwargs))

    def get_dependencies_info(self, chart: Base) -> Dict:
        """获取图表的依赖信息（用于调试）"""
        return self.dep_manager.get_dependencies(chart)


# ========== 兼容 pyecharts_jsdelivr_gh.py 的函数 ==========

def get_dep_url(dep: str) -> str:
    """
    获取依赖对应 jsDelivr GitHub 加速 CDN URL

    Args:
        dep: 依赖名称 (echarts, china, echarts-gl, 等)

    Returns:
        完整的 CDN URL
    """
    manager = JSDependencyManager(DEFAULT_CDN)
    return manager.get_url(dep)


def get_chart_urls(chart: Chart) -> Dict:
    """
    获取图表的所有 jsDelivr GitHub 加速 CDN URL

    Args:
        chart: pyecharts 图表实例

    Returns:
        {
            "dependencies": ["echarts", ...],
            "urls": ["https://cdn.jsdelivr.net/gh/...", ...],
            "html_tags": "<script src=...>...</script>",
            "base_url": chart.cdn_base
        }
    """
    manager = JSDependencyManager(DEFAULT_CDN)
    info = manager.get_dependencies(chart)

    return {
        "dependencies": info["dependencies"],
        "urls": info["cdn_urls"],
        "html_tags": info["html_tags"],
        "base_url": manager.cdn_base
    }


def chart_cdn_info(chart: Chart, chart_name: str = "Chart"):
    """打印图表的 CDN 信息（用于调试）"""
    info = get_chart_urls(chart)
    print(f"\n📊 {chart_name}")
    print("-" * 80)
    print(f"基础地址: {info['base_url']}")
    print(f"依赖: {info['dependencies']}")
    print("CDN 链接:")
    for dep, url in zip(info['dependencies'], info['urls']):
        print(f"  - {dep}: {url}")


# ========== 便捷函数（iframe 渲染相关）==========

def create_renderer(cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None) -> EChartsRenderer:
    """获取或创建 ECharts 渲染器实例"""
    return EChartsRenderer(cdn_provider, custom_cdn_base)


def render_chart(chart: Base, width: str = None, height: str = None,
                 cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None,
                 **kwargs) -> HTML:
    """快速渲染 pyecharts 图表到 iframe"""
    renderer = create_renderer(cdn_provider, custom_cdn_base)
    return renderer.render(chart, width=width, height=height, **kwargs)


def display_chart(chart: Base, **kwargs):
    """快速显示 pyecharts 图表"""
    display(render_chart(chart, **kwargs))


def get_chart_dependencies(chart: Base, cdn_provider: str = DEFAULT_CDN) -> Dict:
    """获取图表所需的 JS 依赖信息（独立函数，用于调试）"""
    manager = JSDependencyManager(cdn_provider)
    return manager.get_dependencies(chart)


# ========== 统一导出 ==========

__all__ = [
    'JSDELIVR_GH_BASE', 'CDN_CONFIGS', 'DEFAULT_CDN', 'RESOURCE_URLS',
    'JSDependencyManager', 'EChartsRenderer',
    'get_dep_url', 'get_chart_urls', 'chart_cdn_info',
    'create_renderer', 'render_chart', 'display_chart', 'get_chart_dependencies',
]


# ========== 使用示例 ==========

if __name__ == "__main__":
    from pyecharts.charts import Bar, Map, Geo, Liquid, WordCloud, Bar3D

    print("=" * 100)
    print("PyECharts Jupyter HTML 导出模块（统一版）")
    print("=" * 100)
    print(f"\n默认 CDN: {JSDELIVR_GH_BASE}\n")

    # 示例 1: 基础图表
    bar = Bar()
    bar.add_xaxis(["A", "B", "C"])
    bar.add_yaxis("", [1, 2, 3])
    chart_cdn_info(bar, "Bar (柱状图)")

    # 示例 2: 中国地图
    map_chart = Map()
    map_chart.add("", [("广东", 100)], "china")
    chart_cdn_info(map_chart, "Map (中国地图)")

    # 示例 3: 水球图
    liquid = Liquid()
    liquid.add("", [0.6])
    chart_cdn_info(liquid, "Liquid (水球图)")

    # 示例 4: 词云图
    wordcloud = WordCloud()
    wordcloud.add("", [("词", 100)])
    chart_cdn_info(wordcloud, "WordCloud (词云图)")

    # 示例 5: 3D 柱状图
    bar3d = Bar3D()
    bar3d.add("", [[0, 0, 1]])
    chart_cdn_info(bar3d, "Bar3D (3D柱状图)")

    print("\n" + "=" * 100)
    print("常用资源快速链接")
    print("=" * 100)
    for name, url in RESOURCE_URLS.items():
        print(f"  {name:<20}: {url}")

    print("\n" + "=" * 100)
    print("快速开始")
    print("=" * 100)
    print("""

# 2. iframe 渲染图表
from pyecharts_jupyter_exporter import render_chart, display_chart
from pyecharts.charts import Bar

bar = Bar()
bar.add_xaxis(["A", "B", "C"])
bar.add_yaxis("Series", [1, 2, 3])

# 渲染为 iframe HTML
display_chart(bar, width="100%", height="500px")

# 3. 获取图表依赖信息
from pyecharts_jupyter_exporter import get_chart_dependencies
info = get_chart_dependencies(bar)
print(info["cdn_urls"])  # 查看 CDN 链接

# 4. 切换 CDN 提供商
from pyecharts_jupyter_exporter import render_chart, CDN_CONFIGS
# 使用 BootCDN
display_chart(bar, cdn_provider="bootcdn")
# 或使用自定义 CDN
display_chart(bar, custom_cdn_base="https://your-cdn.com/assets/")
""")
