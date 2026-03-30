#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pyecharts v2+ jsDelivr GitHub 加速 CDN 配置工具

统一使用: https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/
"""

from pyecharts.charts.chart import Chart
from pyecharts.datasets import FILENAMES
from pyecharts.globals import CurrentConfig
from typing import List, Dict, Optional


# jsDelivr GitHub 加速基础地址
JSDELIVR_GH_BASE = "https://cdn.jsdelivr.net/gh/pyecharts/pyecharts-assets@master/assets/"


def get_jsdelivr_gh_url(dep: str) -> str:
    """
    获取 jsDelivr GitHub 加速 CDN URL

    参数:
        dep: 依赖名称 (echarts, china, echarts-gl, 等)

    返回:
        完整的 CDN URL
    """
    if dep in FILENAMES:
        filename, ext = FILENAMES[dep]
        return f"{JSDELIVR_GH_BASE}{filename}"
    else:
        return f"{JSDELIVR_GH_BASE}{dep}"


def get_chart_cdn_urls(chart: Chart) -> Dict:
    """
    获取图表的所有 jsDelivr GitHub 加速 CDN URL

    参数:
        chart: pyecharts 图表实例

    返回:
        {
            "dependencies": ["echarts", ...],
            "urls": ["https://cdn.jsdelivr.net/gh/...", ...],
            "html_tags": "<script src=...>...</script>"
        }
    """
    deps = list(chart.js_dependencies.items)
    urls = [get_jsdelivr_gh_url(dep) for dep in deps]

    # 生成 HTML script 标签
    html_tags = "\n".join([f'<script src="{url}"></script>' for url in urls])

    return {
        "dependencies": deps,
        "urls": urls,
        "html_tags": html_tags,
        "base_url": JSDELIVR_GH_BASE
    }


def set_jsdelivr_gh_cdn():
    """设置全局 CDN 为 jsDelivr GitHub 加速"""
    CurrentConfig.ONLINE_HOST = JSDELIVR_GH_BASE
    print(f"已设置 CDN 为 jsDelivr GitHub 加速: {JSDELIVR_GH_BASE}")


def print_chart_cdn_info(chart: Chart, chart_name: str = "Chart"):
    """打印图表的 CDN 信息"""
    info = get_chart_cdn_urls(chart)
    print(f"\n📊 {chart_name}")
    print("-" * 80)
    print(f"基础地址: {info['base_url']}")
    print(f"依赖: {info['dependencies']}")
    print("CDN 链接:")
    for dep, url in zip(info['dependencies'], info['urls']):
        print(f"  - {dep}: {url}")


# 常用资源快速访问链接
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


# 使用示例
if __name__ == "__main__":
    from pyecharts.charts import Bar, Map, Geo, Liquid, WordCloud, Bar3D, Line, Pie

    print("=" * 100)
    print("pyecharts v2+ jsDelivr GitHub 加速 CDN 工具")
    print("=" * 100)
    print(f"\n基础地址: {JSDELIVR_GH_BASE}\n")

    # 示例 1: 基础图表
    bar = Bar()
    bar.add_xaxis(["A", "B", "C"])
    bar.add_yaxis("", [1, 2, 3])
    print_chart_cdn_info(bar, "Bar (柱状图)")

    # 示例 2: 中国地图
    map_chart = Map()
    map_chart.add("", [("广东", 100)], "china")
    print_chart_cdn_info(map_chart, "Map (中国地图)")

    # 示例 3: 水球图
    liquid = Liquid()
    liquid.add("", [0.6])
    print_chart_cdn_info(liquid, "Liquid (水球图)")

    # 示例 4: 词云图
    wordcloud = WordCloud()
    wordcloud.add("", [("词", 100)])
    print_chart_cdn_info(wordcloud, "WordCloud (词云图)")

    # 示例 5: 3D 柱状图
    bar3d = Bar3D()
    bar3d.add("", [[0, 0, 1]])
    print_chart_cdn_info(bar3d, "Bar3D (3D柱状图)")

    print("\n" + "=" * 100)
    print("常用资源快速链接")
    print("=" * 100)
    for name, url in RESOURCE_URLS.items():
        print(f"  {name:<20}: {url}")

    print("\n" + "=" * 100)
    print("设置全局 CDN")
    print("=" * 100)
    print("""
在代码中添加以下设置，即可全局使用 jsDelivr GitHub 加速 CDN：

    from pyecharts.globals import CurrentConfig
    from pyecharts_jsdelivr_gh import JSDELIVR_GH_BASE

    CurrentConfig.ONLINE_HOST = JSDELIVR_GH_BASE

或者使用提供的函数：

    from pyecharts_jsdelivr_gh import set_jsdelivr_gh_cdn
    set_jsdelivr_gh_cdn()
""")
