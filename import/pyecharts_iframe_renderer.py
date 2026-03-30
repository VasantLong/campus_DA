"""
PyECharts iframe 渲染器模块（支持动态 JS 依赖）

用于在 Jupyter Notebook 中通过 iframe 沙箱化渲染 pyecharts 图表，
解决 CDN 加载和浏览器追踪防护问题，支持动态分析图表所需的 JS 依赖。
"""

from IPython.display import display, HTML
import html
from typing import Dict, List, Optional, Union

from pyecharts.globals import CurrentConfig, NotebookType
from pyecharts.charts.base import Base
from pyecharts.datasets import FILENAMES

# 配置 Notebook 类型
CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_NOTEBOOK


# ========== CDN 配置 ==========

CDN_CONFIGS = {
    "jsdelivr": "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/",
    "bootcdn": "https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/",
    "pyecharts": "https://assets.pyecharts.org/assets/v6/",
    "staticfile": "https://cdn.staticfile.org/echarts/5.4.3/",
    "kesci": "https://cdn.kesci.com/lib/pyecharts_assets/",
}

DEFAULT_CDN = "jsdelivr"


class JSDependencyManager:
    """
    JS 依赖管理器

    负责分析图表所需的 JS 依赖并生成对应的 CDN URL 和 HTML 标签。
    """

    def __init__(self, cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None):
        """
        初始化依赖管理器

        Args:
            cdn_provider: CDN 提供商名称
            custom_cdn_base: 自定义 CDN 基础 URL
        """
        if custom_cdn_base:
            self.cdn_base = custom_cdn_base
            self.provider = "custom"
        elif cdn_provider in CDN_CONFIGS:
            self.cdn_base = CDN_CONFIGS[cdn_provider]
            self.provider = cdn_provider
        else:
            raise ValueError(f"不支持的 CDN 提供商: {cdn_provider}")

    def get_dependencies(self, chart: Base) -> Dict:
        """
        获取图表所需的 JS 依赖信息

        Returns:
            {
                "dependencies": ["echarts", "china", ...],
                "cdn_urls": ["https://...", ...],
                "html_tags": "<script...>\n<script...>",
                "cdn_provider": "bootcdn",
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
        if self.provider in ["pyecharts", "kesci"]:
            url = f"{self.cdn_base}{file_fullname}"
        else:
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


class EChartsRenderer:
    """
    PyECharts iframe 渲染器（支持动态依赖）
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
        """在 iframe 中渲染 pyecharts 图表"""
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


# ========== 便捷函数 ==========

def get_renderer(cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None) -> EChartsRenderer:
    """获取或创建 ECharts 渲染器实例"""
    return EChartsRenderer(cdn_provider, custom_cdn_base)

def render_chart(chart: Base, width: str = None, height: str = None,
                 cdn_provider: str = DEFAULT_CDN, custom_cdn_base: str = None,
                 **kwargs) -> HTML:
    """快速渲染 pyecharts 图表到 iframe"""
    renderer = get_renderer(cdn_provider, custom_cdn_base)
    return renderer.render(chart, width=width, height=height, **kwargs)

def display_chart(chart: Base, **kwargs):
    """快速显示 pyecharts 图表"""
    display(render_chart(chart, **kwargs))

def render_in_iframe(chart: Base, width: str = None, height: str = None) -> HTML:
    """向后兼容的渲染函数"""
    return render_chart(chart, width=width, height=height)

def get_chart_dependencies(chart: Base, cdn_provider: str = DEFAULT_CDN) -> Dict:
    """获取图表所需的 JS 依赖信息（独立函数，用于调试）"""
    manager = JSDependencyManager(cdn_provider)
    return manager.get_dependencies(chart)

__all__ = [
    'EChartsRenderer', 'JSDependencyManager', 'get_renderer',
    'render_chart', 'display_chart', 'render_in_iframe',
    'get_chart_dependencies', 'CDN_CONFIGS', 'DEFAULT_CDN'
]