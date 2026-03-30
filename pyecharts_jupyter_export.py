from IPython.display import display, HTML
import html
import os
from typing import Optional

from pyecharts.globals import CurrentConfig, NotebookType
from pyecharts.charts.chart import Chart
from pyecharts import options as opts


class PyEchartsJupyterExporter:
    """
    PyEcharts Jupyter导出器，用于在Jupyter环境中渲染和导出包含PyEcharts图表的HTML内容
    使用iframe技术避免浏览器追踪防护，并确保JS依赖只加载一次
    """
    
    def __init__(self, cdn_host: str = "https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/", notebook_type: str = "JUPYTER_NOTEBOOK"):
        """
        初始化PyEchartsJupyterExporter
        
        Args:
            cdn_host: ECharts的CDN地址
            notebook_type: 笔记本类型，默认为JUPYTER_NOTEBOOK
        """
        self.cdn_host = cdn_host
        self.notebook_type = notebook_type
        self._setup_config()
        self._echarts_loaded = False

    def _setup_config(self):
        """设置PyEcharts的全局配置"""
        CurrentConfig.ONLINE_HOST = self.cdn_host
        if self.notebook_type == "JUPYTER_NOTEBOOK":
            CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_NOTEBOOK
        elif self.notebook_type == "JUPYTER_LAB":
            CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB
        else:
            CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB

    def _ensure_echarts_loaded(self):
        """确保 ECharts 已加载到页面"""
        if not self._echarts_loaded:
            display(HTML(f"""
            <script>
                if (typeof window.echarts === 'undefined') {{
                    var script = document.createElement('script');
                    script.src = '{self.cdn_host}echarts.min.js';
                    document.head.appendChild(script);
                    window.__echarts_loading = true;
                }}
            </script>
            """))
            self._echarts_loaded = True

    def render_in_iframe(self, chart) -> HTML:
        """
        在iframe中渲染pyecharts图表，绕过浏览器"Tracking Prevention blocked access to storage"问题
        
        Args:
            chart: pyecharts图表对象
            
        Returns:
            HTML对象，可以直接在Jupyter中显示
        """
        self._ensure_echarts_loaded()
        
        # 获取图表的HTML片段
        html_content = chart.render_embed()
        
        # HTML转义
        escaped_html = html.escape(html_content)
        
        # 动态获取图表的宽高
        width = getattr(chart, 'width', '100%')
        height = getattr(chart, 'height', '500px')
        
        # 创建iframe HTML
        iframe_html = f"""
        <iframe srcdoc="{escaped_html}" 
                width="{width}" 
                height="{height}" 
                frameborder="0"
                scrolling="no"
                sandbox="allow-scripts">
        </iframe>
        """
        return HTML(iframe_html)

    def export_to_html(self, charts, output_path: str, title: str = "PyEcharts Charts Export"):
        """
        将一个或多个图表导出为HTML文件
        
        Args:
            charts: 单个图表对象或图表对象列表
            output_path: 输出HTML文件路径
            title: HTML文档标题
        """
        if not isinstance(charts, list):
            charts = [charts]
        
        # 生成所有图表的iframe HTML
        chart_iframes = []
        for chart in charts:
            iframe = self.render_in_iframe(chart)
            # 提取iframe的HTML内容
            iframe_html = f"""
            <div class="chart-container">
                {iframe.data}
            </div>
            """
            chart_iframes.append(iframe_html)
        
        # 组合完整的HTML文档
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
        .chart-container {{ margin-bottom: 30px; }}
        h1 {{ text-align: center; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {''.join(chart_iframes)}
</body>
</html>"""
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"图表已成功导出至: {output_path}")

    def display_charts(self, *charts):
        """
        在Jupyter中连续显示多个图表
        
        Args:
            *charts: 可变数量的图表对象
        """
        for chart in charts:
            display(self.render_in_iframe(chart))


# 全局实例，方便直接使用
exporter = PyEchartsJupyterExporter()


# 便捷函数，直接调用默认实例的方法
def render_in_iframe(chart):
    """
    在iframe中渲染pyecharts图表
    
    Args:
        chart: pyecharts图表对象
        
    Returns:
        HTML对象，可以在Jupyter中直接显示
    """
    return exporter.render_in_iframe(chart)


def display_charts(*charts):
    """
    在Jupyter中连续显示多个图表
    
    Args:
        *charts: 可变数量的图表对象
    """
    exporter.display_charts(*charts)


def export_charts_to_html(charts, output_path: str, title: str = "PyEcharts Charts Export"):
    """
    将图表导出为HTML文件
    
    Args:
        charts: 单个图表对象或图表对象列表
        output_path: 输出HTML文件路径
        title: HTML文档标题
    """
    exporter.export_to_html(charts, output_path, title)


# 示例使用
if __name__ == "__main__":
    # 创建示例图表
    bar = (
        Bar()
        .add_xaxis(["衬衫", "毛衣", "领带", "裤子", "风衣", "高跟鞋", "袜子"])
        .add_yaxis("商家A", [114, 55, 27, 101, 125, 27, 105])
        .add_yaxis("商家B", [57, 134, 137, 129, 145, 60, 49])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="货品销售情况", subtitle="A和B公司"),
            toolbox_opts=opts.ToolboxOpts(is_show=True)
        )
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .reversal_axis()
    )
    
    # 渲染图表到iframe
    result = render_in_iframe(bar)
    display(result)
    
    # 导出到HTML文件
    export_charts_to_html(bar, "output/example_chart.html", "示例图表")