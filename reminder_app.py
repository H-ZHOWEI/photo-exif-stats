import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS, GPSTAGS
import os
import json
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import rawpy
import exifread
from fractions import Fraction
import re
import threading
import queue


class ImageExifAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("图片EXIF信息统计分析工具")
        self.root.geometry("1400x900")  # 增加窗口宽度以容纳图片和EXIF数据

        # 初始化变量
        self.image_files = []
        self.exif_data_list = []
        self.current_directory = ""
        self.current_image_label = None
        self.current_photo = None
        self.current_image_index = 0
        self.thumbnail_images = {}  # 存储缩略图
        self.thumbnail_buttons = []  # 存储缩略图按钮

        # 缩略图窗口相关
        self.thumbnail_window = None
        self.thumbnail_loading_queue = queue.Queue()

        # EXIF标签翻译字典
        self.exif_translation = {
            'FileName': '文件名',
            'FilePath': '文件路径',
            'ImageWidth': '图像宽度',
            'ImageLength': '图像高度',
            'BitsPerSample': '每样本位数',
            'Compression': '压缩方式',
            'PhotometricInterpretation': '光度解释',
            'Orientation': '方向',
            'SamplesPerPixel': '每像素样本数',
            'PlanarConfiguration': '平面配置',
            'YCbCrSubSampling': 'YCbCr子采样',
            'YCbCrPositioning': 'YCbCr定位',
            'XResolution': '水平分辨率',
            'YResolution': '垂直分辨率',
            'ResolutionUnit': '分辨率单位',
            'StripOffsets': '条带偏移',
            'RowsPerStrip': '每带行数',
            'StripByteCounts': '条带字节数',
            'JPEGInterchangeFormat': 'JPEG交换格式',
            'JPEGInterchangeFormatLength': 'JPEG交换格式长度',
            'TransferFunction': '传递函数',
            'WhitePoint': '白点',
            'PrimaryChromaticities': '主要色度',
            'YCbCrCoefficients': 'YCbCr系数',
            'ReferenceBlackWhite': '参考黑白色',
            'DateTime': '修改时间',
            'ImageDescription': '图像描述',
            'Make': '制造商',
            'Model': '相机型号',
            'Software': '软件',
            'Artist': '作者',
            'Copyright': '版权',
            'ExifOffset': 'Exif偏移',
            'GPSInfo': 'GPS信息',
            'ExposureTime': '曝光时间',
            'FNumber': '光圈值',
            'ExposureProgram': '曝光程序',
            'ISOSpeedRatings': '感光度',
            'ExifVersion': 'Exif版本',
            'DateTimeOriginal': '拍摄时间',
            'DateTimeDigitized': '数字化时间',
            'ComponentsConfiguration': '组件配置',
            'CompressedBitsPerPixel': '压缩每像素位数',
            'ShutterSpeedValue': '快门速度值',
            'ApertureValue': '光圈值',
            'BrightnessValue': '亮度值',
            'ExposureBiasValue': '曝光补偿',
            'MaxApertureValue': '最大光圈值',
            'SubjectDistance': '主体距离',
            'MeteringMode': '测光模式',
            'LightSource': '光源',
            'Flash': '闪光灯',
            'FocalLength': '焦距',
            'SubjectArea': '主体区域',
            'MakerNote': '制造商注释',
            'UserComment': '用户注释',
            'SubSecTime': '亚秒时间',
            'SubSecTimeOriginal': '原始亚秒时间',
            'SubSecTimeDigitized': '数字化亚秒时间',
            'FlashpixVersion': 'Flashpix版本',
            'ColorSpace': '色彩空间',
            'PixelXDimension': '像素X维度',
            'PixelYDimension': '像素Y维度',
            'RelatedSoundFile': '相关音频文件',
            'InteroperabilityOffset': '互操作性偏移',
            'FocalPlaneXResolution': '焦平面X分辨率',
            'FocalPlaneYResolution': '焦平面Y分辨率',
            'FocalPlaneResolutionUnit': '焦平面分辨率单位',
            'SensingMethod': '感光方法',
            'FileSource': '文件来源',
            'SceneType': '场景类型',
            'CFAPattern': 'CFA图案',
            'CustomRendered': '自定义渲染',
            'ExposureMode': '曝光模式',
            'WhiteBalance': '白平衡',
            'DigitalZoomRatio': '数码变焦比率',
            'FocalLengthIn35mmFilm': '35mm等效焦距',
            'SceneCaptureType': '场景捕捉类型',
            'GainControl': '增益控制',
            'Contrast': '对比度',
            'Saturation': '饱和度',
            'Sharpness': '锐度',
            'DeviceSettingDescription': '设备设置描述',
            'SubjectDistanceRange': '主体距离范围',
            'ImageUniqueID': '图像唯一ID',
            'LensMake': '镜头制造商',
            'LensModel': '镜头型号',
            'LensSerialNumber': '镜头序列号',
            'Gamma': '伽马值',
            'GPSVersionID': 'GPS版本',
            'GPSLatitudeRef': 'GPS纬度参考',
            'GPSLatitude': 'GPS纬度',
            'GPSLongitudeRef': 'GPS经度参考',
            'GPSLongitude': 'GPS经度',
            'GPSAltitudeRef': 'GPS海拔参考',
            'GPSAltitude': 'GPS海拔',
            'GPSTimeStamp': 'GPS时间戳',
            'GPSSatellites': 'GPS卫星',
            'GPSStatus': 'GPS状态',
            'GPSMeasureMode': 'GPS测量模式',
            'GPSDOP': 'GPS精度',
            'GPSSpeedRef': 'GPS速度参考',
            'GPSSpeed': 'GPS速度',
            'GPSTrackRef': 'GPS轨迹参考',
            'GPSTrack': 'GPS轨迹',
            'GPSImgDirectionRef': 'GPS图像方向参考',
            'GPSImgDirection': 'GPS图像方向',
            'GPSMapDatum': 'GPS地图基准',
            'GPSDestLatitudeRef': 'GPS目标纬度参考',
            'GPSDestLatitude': 'GPS目标纬度',
            'GPSDestLongitudeRef': 'GPS目标经度参考',
            'GPSDestLongitude': 'GPS目标经度',
            'GPSDestBearingRef': 'GPS目标方位参考',
            'GPSDestBearing': 'GPS目标方位',
            'GPSDestDistanceRef': 'GPS目标距离参考',
            'GPSDestDistance': 'GPS目标距离',
            'GPSProcessingMethod': 'GPS处理方法',
            'GPSAreaInformation': 'GPS区域信息',
            'GPSDateStamp': 'GPS日期戳',
            'GPSDifferential': 'GPS差分',
            'GPSHPositioningError': 'GPS水平定位误差',
            '焦距': '焦距',
            '光圈值': '光圈值',
            'ISO': '感光度',
            '曝光时间': '曝光时间',
            '相机型号': '相机型号',
            '拍摄时间': '拍摄时间',
            '镜头型号': '镜头型号',
            '制造商': '制造商'
        }

        # 设置中文字体支持
        self.setup_chinese_font()

        # 设置样式
        self.setup_styles()

        # 创建界面
        self.create_widgets()

        # 绑定键盘事件
        self.bind_keyboard_events()

        # 启动缩略图队列处理
        self.process_thumbnail_queue()

    def setup_chinese_font(self):
        """设置中文字体支持"""
        try:
            # 尝试多种中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置颜色
        self.bg_color = "#f0f0f0"
        self.frame_bg = "#ffffff"
        self.button_color = "#4a6fa5"

        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="图片EXIF信息统计分析工具",
            font=("Microsoft YaHei", 16, "bold"),
            foreground="#2c3e50"
        )
        title_label.grid(row=0, column=0, pady=(0, 15), sticky=tk.W)

        # 控制面板框架
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        # 选择文件夹按钮
        ttk.Label(control_frame, text="图片文件夹:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.dir_label = ttk.Label(control_frame, text="未选择文件夹", foreground="gray", width=40)
        self.dir_label.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

        browse_btn = ttk.Button(control_frame, text="选择文件夹", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=(0, 10))

        # 加载按钮
        load_btn = ttk.Button(control_frame, text="加载图片", command=self.load_images)
        load_btn.grid(row=0, column=3, padx=(0, 10))

        # 缩略图浏览器按钮
        self.thumbnail_btn = ttk.Button(control_frame, text="缩略图浏览器", command=self.show_thumbnail_browser,
                                        state="disabled")
        self.thumbnail_btn.grid(row=0, column=4, padx=(0, 10))

        # 统计选项框架
        stats_frame = ttk.LabelFrame(main_frame, text="统计选项", padding="10")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)

        # 创建标签页控件
        self.notebook = ttk.Notebook(stats_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建各个标签页
        self.create_stats_tabs()

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def create_stats_tabs(self):
        """创建统计标签页"""
        # 焦距统计标签页
        focal_length_tab = ttk.Frame(self.notebook)
        self.notebook.add(focal_length_tab, text="焦距统计")
        self.create_focal_length_tab(focal_length_tab)

        # 快门速度统计标签页（实际统计曝光时间）
        shutter_speed_tab = ttk.Frame(self.notebook)
        self.notebook.add(shutter_speed_tab, text="快门速度统计")
        self.create_shutter_speed_tab(shutter_speed_tab)

        # 光圈统计标签页
        aperture_tab = ttk.Frame(self.notebook)
        self.notebook.add(aperture_tab, text="光圈统计")
        self.create_aperture_tab(aperture_tab)

        # ISO统计标签页
        iso_tab = ttk.Frame(self.notebook)
        self.notebook.add(iso_tab, text="ISO统计")
        self.create_iso_tab(iso_tab)

        # 相机型号统计标签页
        camera_tab = ttk.Frame(self.notebook)
        self.notebook.add(camera_tab, text="相机型号统计")
        self.create_camera_tab(camera_tab)

        # 拍摄时间统计标签页
        datetime_tab = ttk.Frame(self.notebook)
        self.notebook.add(datetime_tab, text="拍摄时间统计")
        self.create_datetime_tab(datetime_tab)

        # 原始数据标签页
        raw_data_tab = ttk.Frame(self.notebook)
        self.notebook.add(raw_data_tab, text="原始EXIF数据")
        self.create_raw_data_tab(raw_data_tab)

    def create_focal_length_tab(self, parent):
        """创建焦距统计标签页"""
        # 框架
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 焦距分组选项
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(options_frame, text="焦距分组方式:").pack(side=tk.LEFT, padx=(0, 5))

        self.focal_group_var = tk.StringVar(value="range")
        ttk.Radiobutton(
            options_frame, text="按范围分组",
            variable=self.focal_group_var, value="range"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame, text="按具体值分组",
            variable=self.focal_group_var, value="exact"
        ).pack(side=tk.LEFT)

        # 统计按钮
        ttk.Button(
            options_frame, text="统计焦距",
            command=lambda: self.analyze_focal_length()
        ).pack(side=tk.RIGHT)

        # 结果显示区域
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧为文本统计结果
        text_frame = ttk.LabelFrame(results_frame, text="统计结果", padding="10")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 添加滚动条
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.focal_text = tk.Text(text_frame, height=20, yscrollcommand=text_scroll.set)
        self.focal_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.focal_text.yview)

        # 右侧为图表
        chart_frame = ttk.LabelFrame(results_frame, text="图表", padding="10")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.focal_chart_frame = ttk.Frame(chart_frame)
        self.focal_chart_frame.pack(fill=tk.BOTH, expand=True)

    def create_shutter_speed_tab(self, parent):
        """创建快门速度统计标签页（实际统计曝光时间）"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 统计按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            btn_frame, text="统计快门速度",
            command=lambda: self.analyze_exposure_time()
        ).pack(side=tk.RIGHT)

        # 结果显示区域
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧为文本统计结果
        text_frame = ttk.LabelFrame(results_frame, text="统计结果", padding="10")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 添加滚动条
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.shutter_text = tk.Text(text_frame, height=20, yscrollcommand=text_scroll.set)
        self.shutter_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.shutter_text.yview)

        # 右侧为图表
        chart_frame = ttk.LabelFrame(results_frame, text="图表", padding="10")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.shutter_chart_frame = ttk.Frame(chart_frame)
        self.shutter_chart_frame.pack(fill=tk.BOTH, expand=True)

    def create_aperture_tab(self, parent):
        """创建光圈统计标签页"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 统计按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            btn_frame, text="统计光圈值",
            command=lambda: self.analyze_aperture()
        ).pack(side=tk.RIGHT)

        # 结果显示区域
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧为文本统计结果
        text_frame = ttk.LabelFrame(results_frame, text="统计结果", padding="10")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 添加滚动条
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.aperture_text = tk.Text(text_frame, height=20, yscrollcommand=text_scroll.set)
        self.aperture_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.aperture_text.yview)

        # 右侧为图表
        chart_frame = ttk.LabelFrame(results_frame, text="图表", padding="10")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.aperture_chart_frame = ttk.Frame(chart_frame)
        self.aperture_chart_frame.pack(fill=tk.BOTH, expand=True)

    def create_iso_tab(self, parent):
        """创建ISO统计标签页"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 统计按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            btn_frame, text="统计ISO值",
            command=lambda: self.analyze_iso()
        ).pack(side=tk.RIGHT)

        # 结果显示区域
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧为文本统计结果
        text_frame = ttk.LabelFrame(results_frame, text="统计结果", padding="10")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 添加滚动条
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.iso_text = tk.Text(text_frame, height=20, yscrollcommand=text_scroll.set)
        self.iso_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.iso_text.yview)

        # 右侧为图表
        chart_frame = ttk.LabelFrame(results_frame, text="图表", padding="10")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.iso_chart_frame = ttk.Frame(chart_frame)
        self.iso_chart_frame.pack(fill=tk.BOTH, expand=True)

    def create_camera_tab(self, parent):
        """创建相机型号统计标签页"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 统计按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            btn_frame, text="统计相机型号",
            command=lambda: self.analyze_camera()
        ).pack(side=tk.RIGHT)

        # 结果显示区域
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧为文本统计结果
        text_frame = ttk.LabelFrame(results_frame, text="统计结果", padding="10")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 添加滚动条
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.camera_text = tk.Text(text_frame, height=20, yscrollcommand=text_scroll.set)
        self.camera_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.camera_text.yview)

        # 右侧为图表
        chart_frame = ttk.LabelFrame(results_frame, text="图表", padding="10")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.camera_chart_frame = ttk.Frame(chart_frame)
        self.camera_chart_frame.pack(fill=tk.BOTH, expand=True)

    def create_datetime_tab(self, parent):
        """创建拍摄时间统计标签页"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 分组选项
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(options_frame, text="时间分组方式:").pack(side=tk.LEFT, padx=(0, 5))

        self.datetime_group_var = tk.StringVar(value="year")
        ttk.Radiobutton(
            options_frame, text="按年",
            variable=self.datetime_group_var, value="year"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame, text="按月",
            variable=self.datetime_group_var, value="month"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame, text="按小时",
            variable=self.datetime_group_var, value="hour"
        ).pack(side=tk.LEFT)

        # 统计按钮
        ttk.Button(
            options_frame, text="统计拍摄时间",
            command=lambda: self.analyze_datetime()
        ).pack(side=tk.RIGHT)

        # 结果显示区域
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧为文本统计结果
        text_frame = ttk.LabelFrame(results_frame, text="统计结果", padding="10")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 添加滚动条
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.datetime_text = tk.Text(text_frame, height=20, yscrollcommand=text_scroll.set)
        self.datetime_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.datetime_text.yview)

        # 右侧为图表
        chart_frame = ttk.LabelFrame(results_frame, text="图表", padding="10")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.datetime_chart_frame = ttk.Frame(chart_frame)
        self.datetime_chart_frame.pack(fill=tk.BOTH, expand=True)

    def create_raw_data_tab(self, parent):
        """创建原始EXIF数据标签页 - 修改为左边显示图片，右边显示EXIF数据"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 配置frame的网格权重
        frame.columnconfigure(0, weight=1)  # 左侧图片区域
        frame.columnconfigure(1, weight=2)  # 右侧EXIF数据区域
        frame.rowconfigure(1, weight=1)

        # 顶部控制区域
        control_frame = ttk.Frame(frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 导航控制
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(nav_frame, text="◀ 上一张", command=self.prev_image, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="下一张 ▶", command=self.next_image, width=10).pack(side=tk.LEFT)

        # 图片选择
        select_frame = ttk.Frame(control_frame)
        select_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(select_frame, text="选择图片:").pack(side=tk.LEFT, padx=(0, 5))

        # 图片选择下拉框
        self.image_var = tk.StringVar()
        self.image_combo = ttk.Combobox(select_frame, textvariable=self.image_var, state="readonly", width=50)
        self.image_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.image_combo.bind("<<ComboboxSelected>>", self.display_image_with_exif)

        # 显示按钮
        ttk.Button(control_frame, text="显示EXIF数据", command=self.display_image_with_exif).pack(side=tk.LEFT,
                                                                                                  padx=(0, 10))

        # 导出按钮
        ttk.Button(control_frame, text="导出所有数据", command=self.export_all_data).pack(side=tk.RIGHT)

        # 左侧图片显示区域
        left_frame = ttk.LabelFrame(frame, text="图片预览 (使用← →键切换图片)", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        # 图片显示画布
        self.image_canvas = tk.Canvas(left_frame, bg="gray", highlightthickness=0)
        self.image_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 右侧EXIF数据显示区域
        right_frame = ttk.LabelFrame(frame, text="EXIF数据明细（已翻译）", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 创建Treeview显示EXIF数据
        columns = ('tag', 'value')
        self.exif_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=20)

        # 定义列
        self.exif_tree.heading('tag', text='标签名称')
        self.exif_tree.heading('value', text='值')
        self.exif_tree.column('tag', width=200, anchor=tk.W)
        self.exif_tree.column('value', width=300, anchor=tk.W)

        # 添加滚动条
        tree_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.exif_tree.yview)
        self.exif_tree.configure(yscrollcommand=tree_scroll.set)

        self.exif_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def bind_keyboard_events(self):
        """绑定键盘事件"""
        self.root.bind('<Left>', self.on_left_key)
        self.root.bind('<Right>', self.on_right_key)

        # 绑定到特定控件上
        self.image_canvas.bind('<Left>', self.on_left_key)
        self.image_canvas.bind('<Right>', self.on_right_key)
        self.exif_tree.bind('<Left>', self.on_left_key)
        self.exif_tree.bind('<Right>', self.on_right_key)

    def on_left_key(self, event=None):
        """左键事件 - 切换到上一张图片"""
        if self.image_files:
            self.prev_image()
        return "break"  # 防止事件继续传播

    def on_right_key(self, event=None):
        """右键事件 - 切换到下一张图片"""
        if self.image_files:
            self.next_image()
        return "break"  # 防止事件继续传播

    def prev_image(self):
        """显示上一张图片"""
        if not self.image_files:
            return

        self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
        self.image_combo.current(self.current_image_index)
        self.display_image_with_exif()

    def next_image(self):
        """显示下一张图片"""
        if not self.image_files:
            return

        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.image_combo.current(self.current_image_index)
        self.display_image_with_exif()

    def browse_folder(self):
        """选择文件夹"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        if folder_path:
            self.current_directory = folder_path
            self.dir_label.config(text=folder_path)
            self.status_var.set(f"已选择文件夹: {folder_path}")

    def load_images(self):
        """加载图片并提取EXIF数据"""
        if not self.current_directory:
            messagebox.showwarning("警告", "请先选择图片文件夹")
            return

        # 清空之前的数据
        self.image_files = []
        self.exif_data_list = []
        self.thumbnail_images.clear()
        self.thumbnail_buttons.clear()
        self.current_image_index = 0

        # 支持的图片格式（包括CR3）
        supported_formats = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif', '.cr3', '.cr2', '.nef', '.arw', '.dng')

        # 遍历文件夹中的图片文件
        self.status_var.set("正在加载图片...")
        self.root.update()

        for root_dir, dirs, files in os.walk(self.current_directory):
            for file in files:
                if file.lower().endswith(supported_formats):
                    file_path = os.path.join(root_dir, file)
                    self.image_files.append(file_path)

        if not self.image_files:
            messagebox.showwarning("警告", "选择的文件夹中没有找到支持的图片文件")
            self.status_var.set("未找到图片文件")
            return

        # 提取EXIF数据
        self.status_var.set(f"正在提取EXIF数据 (0/{len(self.image_files)})...")
        self.root.update()

        exif_count = 0
        for i, file_path in enumerate(self.image_files):
            try:
                file_ext = os.path.splitext(file_path)[1].lower()
                exif_data = {}

                # 首先尝试使用exifread提取所有EXIF数据（这能得到较好的快门速度格式）
                exifread_data = self.extract_exif_with_exifread(file_path)
                if exifread_data:
                    exif_data.update(exifread_data)

                # 然后尝试使用PIL提取EXIF数据（主要是为了获得格式化的光圈值）
                # 但只提取光圈值，其他数据保留exifread的
                pil_exif = self.extract_exif_with_pil(file_path)
                if pil_exif and '光圈值' in pil_exif:
                    # 使用PIL格式化的光圈值替换exifread的原始光圈值
                    exif_data['光圈值'] = pil_exif['光圈值']

                # 如果PIL提取到了焦距但exifread没有，也使用PIL的
                if pil_exif and '焦距' in pil_exif and '焦距' not in exif_data:
                    exif_data['焦距'] = pil_exif['焦距']

                if exif_data:
                    # 添加文件名和路径
                    exif_data['FileName'] = os.path.basename(file_path)
                    exif_data['FilePath'] = file_path

                    self.exif_data_list.append(exif_data)
                    exif_count += 1

                if i % 10 == 0:
                    self.status_var.set(f"正在提取EXIF数据 ({i}/{len(self.image_files)})...")
                    self.root.update()

            except Exception as e:
                print(f"无法读取 {file_path}: {e}")

        # 更新图片选择下拉框
        self.image_combo['values'] = [os.path.basename(f) for f in self.image_files]
        if self.image_files:
            self.image_combo.current(0)

        # 启用缩略图浏览器按钮
        self.thumbnail_btn.config(state="normal")

        # 开始异步加载缩略图
        self.load_thumbnails_async()

        self.status_var.set(f"成功加载 {len(self.image_files)} 张图片，其中 {exif_count} 张包含EXIF数据")

        # 显示加载完成消息
        messagebox.showinfo("加载完成", f"成功加载 {len(self.image_files)} 张图片，其中 {exif_count} 张包含EXIF数据")

    def load_thumbnails_async(self):
        """异步加载缩略图"""
        # 启动线程加载缩略图
        thread = threading.Thread(target=self.load_thumbnails_thread, daemon=True)
        thread.start()

    def load_thumbnails_thread(self):
        """在后台线程中加载缩略图"""
        thumbnail_size = (100, 100)  # 缩略图大小

        for i, file_path in enumerate(self.image_files):
            try:
                # 加载图片并创建缩略图
                img = Image.open(file_path)
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # 将缩略图添加到队列中，在主线程中处理
                self.thumbnail_loading_queue.put((i, file_path, photo))

            except Exception as e:
                print(f"无法创建缩略图 {file_path}: {e}")
                # 添加一个占位符
                placeholder = Image.new('RGB', thumbnail_size, color='gray')
                photo = ImageTk.PhotoImage(placeholder)
                self.thumbnail_loading_queue.put((i, file_path, photo))

    def process_thumbnail_queue(self):
        """处理缩略图加载队列"""
        try:
            while not self.thumbnail_loading_queue.empty():
                i, file_path, photo = self.thumbnail_loading_queue.get_nowait()
                self.thumbnail_images[file_path] = photo

                # 如果缩略图窗口存在，更新按钮
                if self.thumbnail_window and self.thumbnail_window.winfo_exists():
                    self.create_thumbnail_button(i, file_path, photo)

        except queue.Empty:
            pass

        # 每100毫秒检查一次队列
        self.root.after(100, self.process_thumbnail_queue)

    def show_thumbnail_browser(self):
        """显示缩略图浏览器窗口"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先加载图片")
            return

        # 如果窗口已存在，则显示它
        if self.thumbnail_window and self.thumbnail_window.winfo_exists():
            self.thumbnail_window.deiconify()
            self.thumbnail_window.focus()
            return

        # 创建新窗口
        self.thumbnail_window = tk.Toplevel(self.root)
        self.thumbnail_window.title("缩略图浏览器")
        self.thumbnail_window.geometry("800x600")

        # 设置窗口图标
        try:
            self.thumbnail_window.iconbitmap(default='')
        except:
            pass

        # 创建框架
        main_frame = ttk.Frame(self.thumbnail_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 添加标题和说明
        title_label = ttk.Label(
            main_frame,
            text=f"缩略图浏览器 ({len(self.image_files)} 张图片)",
            font=("Microsoft YaHei", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 添加滚动条框架
        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        # 创建画布和滚动条
        canvas = tk.Canvas(scroll_frame, bg="white")
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)

        # 创建内部框架用于放置缩略图
        self.thumbnail_container = ttk.Frame(canvas)
        self.thumbnail_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # 将内部框架添加到画布
        canvas.create_window((0, 0), window=self.thumbnail_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局画布和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 创建缩略图按钮
        self.create_thumbnail_buttons()

        # 窗口关闭事件
        def on_closing():
            self.thumbnail_window.destroy()
            self.thumbnail_window = None

        self.thumbnail_window.protocol("WM_DELETE_WINDOW", on_closing)

    def create_thumbnail_buttons(self):
        """创建缩略图按钮"""
        # 清空之前的按钮
        for widget in self.thumbnail_container.winfo_children():
            widget.destroy()

        self.thumbnail_buttons.clear()

        # 设置每行的缩略图数量
        thumbnails_per_row = 6

        # 创建缩略图按钮
        for i, file_path in enumerate(self.image_files):
            # 获取缩略图
            if file_path in self.thumbnail_images:
                photo = self.thumbnail_images[file_path]
            else:
                # 如果还没有缩略图，创建一个占位符
                placeholder = Image.new('RGB', (100, 100), color='gray')
                photo = ImageTk.PhotoImage(placeholder)
                self.thumbnail_images[file_path] = photo

            # 创建按钮框架
            btn_frame = ttk.Frame(self.thumbnail_container)
            btn_frame.grid(row=i // thumbnails_per_row, column=i % thumbnails_per_row, padx=5, pady=5)

            # 创建按钮
            btn = tk.Button(
                btn_frame,
                image=photo,
                command=lambda idx=i: self.select_image_from_thumbnail(idx),
                relief="flat",
                bg="white",
                activebackground="#e0e0e0"
            )
            btn.pack()

            # 添加文件名标签（截断过长的文件名）
            filename = os.path.basename(file_path)
            if len(filename) > 15:
                filename = filename[:12] + "..."

            label = ttk.Label(btn_frame, text=filename, wraplength=100)
            label.pack(pady=(2, 0))

            # 保存按钮引用
            self.thumbnail_buttons.append(btn)

            # 保存图片索引
            btn.image_index = i

            # 如果是当前显示的图片，添加边框
            if i == self.current_image_index:
                btn.config(relief="solid", borderwidth=2)

    def create_thumbnail_button(self, index, file_path, photo):
        """创建单个缩略图按钮"""
        # 计算位置
        thumbnails_per_row = 6
        row = index // thumbnails_per_row
        col = index % thumbnails_per_row

        # 创建按钮框架
        btn_frame = ttk.Frame(self.thumbnail_container)
        btn_frame.grid(row=row, column=col, padx=5, pady=5)

        # 创建按钮
        btn = tk.Button(
            btn_frame,
            image=photo,
            command=lambda idx=index: self.select_image_from_thumbnail(idx),
            relief="flat",
            bg="white",
            activebackground="#e0e0e0"
        )
        btn.pack()

        # 添加文件名标签
        filename = os.path.basename(file_path)
        if len(filename) > 15:
            filename = filename[:12] + "..."

        label = ttk.Label(btn_frame, text=filename, wraplength=100)
        label.pack(pady=(2, 0))

        # 保存按钮引用
        if index < len(self.thumbnail_buttons):
            # 替换现有的按钮
            old_frame = self.thumbnail_buttons[index].master
            old_frame.destroy()
            self.thumbnail_buttons[index] = btn
        else:
            self.thumbnail_buttons.append(btn)

        # 保存图片索引
        btn.image_index = index

        # 如果是当前显示的图片，添加边框
        if index == self.current_image_index:
            btn.config(relief="solid", borderwidth=2)

    def select_image_from_thumbnail(self, index):
        """从缩略图选择图片"""
        if 0 <= index < len(self.image_files):
            # 切换到原始EXIF数据标签页
            self.notebook.select(6)  # 第7个标签页（索引6）

            # 更新当前图片索引
            self.current_image_index = index

            # 更新下拉框选择
            self.image_combo.current(index)

            # 显示图片
            self.display_image_with_exif()

            # 更新缩略图窗口中的选中状态
            if self.thumbnail_window and self.thumbnail_window.winfo_exists():
                self.update_thumbnail_selection()

            # 将焦点返回到主窗口
            self.root.focus()

    def update_thumbnail_selection(self):
        """更新缩略图选中状态"""
        for i, btn in enumerate(self.thumbnail_buttons):
            if i == self.current_image_index:
                btn.config(relief="solid", borderwidth=2)
            else:
                btn.config(relief="flat", borderwidth=0)

    def extract_exif_with_pil(self, file_path):
        """使用PIL提取图片的EXIF数据"""
        try:
            exif_data = {}
            with Image.open(file_path) as img:
                exif = img._getexif()
                if exif:
                    # 将EXIF标签ID转换为可读的名称
                    for tag_id, value in exif.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        # 特殊处理一些常见的标签
                        if tag_name == 'FNumber':
                            # 处理光圈值 - 保持原来的格式化逻辑
                            if isinstance(value, tuple):
                                # 如果是元组（分数形式），计算小数
                                try:
                                    aperture_value = value[0] / value[1]
                                    # 四舍五入到一位小数
                                    aperture_value = round(aperture_value, 1)
                                    exif_data['光圈值'] = f"f/{aperture_value}"
                                except:
                                    exif_data['光圈值'] = str(value)
                            else:
                                exif_data['光圈值'] = f"f/{value}"
                        elif tag_name == 'ExposureTime':
                            # 处理曝光时间 - 但这里我们主要用exifread的，所以可以简单处理
                            if isinstance(value, tuple):
                                try:
                                    exposure_value = value[0] / value[1]
                                    if exposure_value < 1:
                                        exif_data['曝光时间'] = f"{value[0]}/{value[1]}"
                                    else:
                                        exif_data['曝光时间'] = str(value[0])
                                except:
                                    exif_data['曝光时间'] = str(value)
                            else:
                                exif_data['曝光时间'] = str(value)
                        elif tag_name == 'FocalLength':
                            # 处理焦距
                            if isinstance(value, tuple):
                                try:
                                    focal_value = value[0] / value[1]
                                    exif_data['焦距'] = f"{focal_value}mm"
                                except:
                                    exif_data['焦距'] = str(value)
                            else:
                                exif_data['焦距'] = f"{value}mm"
                        elif tag_name == 'ISOSpeedRatings':
                            # 处理ISO
                            exif_data['ISO'] = str(value)
                        elif tag_name == 'Model':
                            exif_data['相机型号'] = str(value)
                        elif tag_name == 'DateTimeOriginal':
                            exif_data['拍摄时间'] = str(value)
                        elif tag_name == 'DateTime':
                            if '拍摄时间' not in exif_data:
                                exif_data['拍摄时间'] = str(value)
                        elif tag_name == 'LensModel':
                            exif_data['镜头型号'] = str(value)
                        elif tag_name == 'Make':
                            exif_data['制造商'] = str(value)

            return exif_data
        except Exception as e:
            print(f"使用PIL处理文件 {file_path} 时出错: {e}")
            return {}

    def extract_exif_with_exifread(self, file_path):
        """使用exifread提取图片的EXIF数据"""
        try:
            exif_data = {}
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)

                for tag in tags.keys():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                        tag_name = str(tag)
                        value = str(tags[tag])

                        # 处理常见的EXIF字段
                        if 'ExposureTime' in tag or '曝光时间' in tag or 'Exposure Time' in tag:
                            exif_data['曝光时间'] = value
                        elif 'FNumber' in tag or 'ApertureValue' in tag or '光圈值' in tag:
                            exif_data['光圈值'] = value
                        elif 'FocalLengthIn35mmFilm' in tag:
                            # 35mm 等效焦距单独存放，避免覆盖实际焦距
                            exif_data['等效焦距'] = value
                        elif 'FocalLength' in tag or '焦距' in tag:
                            exif_data['焦距'] = value
                        elif 'ISOSpeedRatings' in tag or 'ISO' in tag or '感光度' in tag:
                            exif_data['ISO'] = value
                        # 注意：LensModel 里也含 "Model"，必须先判断镜头，否则机身型号会被镜头型号覆盖
                        elif 'LensModel' in tag or 'Lens' in tag:
                            exif_data['镜头型号'] = value
                        elif 'Model' in tag or 'Camera Model Name' in tag:
                            exif_data['相机型号'] = value
                        elif 'DateTimeOriginal' in tag or 'DateTimeDigitized' in tag or 'CreateDate' in tag:
                            # 拍摄时间优先，且不被后面的「修改时间」覆盖
                            exif_data['拍摄时间'] = value
                        elif 'DateTime' in tag:
                            # 只有拿不到拍摄时间时，才用文件时间兜底
                            exif_data.setdefault('拍摄时间', value)
                        elif 'Make' in tag or 'Manufacturer' in tag:
                            exif_data['制造商'] = value
                        else:
                            # 其他标签使用原始标签名
                            exif_data[tag_name] = value

            return exif_data
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            return {}

    def analyze_focal_length(self):
        """分析焦距统计"""
        if not self.exif_data_list:
            messagebox.showwarning("警告", "请先加载图片")
            return

        # 提取所有焦距数据
        focal_lengths = []
        for exif in self.exif_data_list:
            focal_length = exif.get('焦距')

            if focal_length:
                try:
                    # 处理焦距值，转换为浮点数
                    focal_float = self.parse_exif_value(focal_length)
                    if focal_float is not None:
                        focal_lengths.append(focal_float)
                except Exception as e:
                    print(f"处理焦距数据时出错: {e}")

        if not focal_lengths:
            messagebox.showinfo("信息", "没有找到焦距数据")
            return

        # 清除之前的图表
        for widget in self.focal_chart_frame.winfo_children():
            widget.destroy()

        # 清除文本区域
        self.focal_text.delete(1.0, tk.END)

        # 根据分组方式处理数据
        if self.focal_group_var.get() == "range":
            # 按范围分组
            ranges = {
                '超广角 (<20mm)': 0,
                '广角 (20-35mm)': 0,
                '标准 (35-70mm)': 0,
                '中长焦 (70-135mm)': 0,
                '长焦 (135-300mm)': 0,
                '超长焦 (>300mm)': 0
            }

            for focal in focal_lengths:
                if focal < 20:
                    ranges['超广角 (<20mm)'] += 1
                elif focal < 35:
                    ranges['广角 (20-35mm)'] += 1
                elif focal < 70:
                    ranges['标准 (35-70mm)'] += 1
                elif focal < 135:
                    ranges['中长焦 (70-135mm)'] += 1
                elif focal < 300:
                    ranges['长焦 (135-300mm)'] += 1
                else:
                    ranges['超长焦 (>300mm)'] += 1

            # 显示文本结果
            self.focal_text.insert(tk.END, "焦距范围统计:\n")
            self.focal_text.insert(tk.END, "=" * 40 + "\n")
            total = len(focal_lengths)
            for range_name, count in ranges.items():
                if count > 0:
                    percentage = (count / total) * 100
                    self.focal_text.insert(tk.END, f"{range_name}: {count} 张 ({percentage:.1f}%)\n")

            # 创建图表
            fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
            labels = [k for k, v in ranges.items() if v > 0]
            values = [v for v in ranges.values() if v > 0]

            if labels:
                ax.bar(labels, values, color=plt.cm.Set3(np.arange(len(labels))))
                ax.set_title('焦距范围分布')
                ax.set_ylabel('图片数量')
                ax.tick_params(axis='x', rotation=45)
                plt.tight_layout()

                # 在Tkinter中显示图表
                canvas = FigureCanvasTkAgg(fig, self.focal_chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # 按具体值分组
            # 四舍五入到最接近的整数
            rounded_focals = [round(f) for f in focal_lengths]
            counter = Counter(rounded_focals)

            # 显示文本结果
            self.focal_text.insert(tk.END, "具体焦距统计:\n")
            self.focal_text.insert(tk.END, "=" * 40 + "\n")
            for focal, count in sorted(counter.items(), key=lambda x: x[0]):
                percentage = (count / len(focal_lengths)) * 100
                self.focal_text.insert(tk.END, f"{focal}mm: {count} 张 ({percentage:.1f}%)\n")

            # 创建图表
            fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
            # 只显示前15个最常用的焦距
            sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:15]
            labels = [f"{focal}mm" for focal, count in sorted_items]
            values = [count for focal, count in sorted_items]

            ax.bar(labels, values, color=plt.cm.Set3(np.arange(len(labels))))
            ax.set_title('常用焦距统计 (前15)')
            ax.set_ylabel('图片数量')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()

            # 在Tkinter中显示图表
            canvas = FigureCanvasTkAgg(fig, self.focal_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def analyze_exposure_time(self):
        """分析曝光时间统计（显示为快门速度统计）"""
        if not self.exif_data_list:
            messagebox.showwarning("警告", "请先加载图片")
            return

        # 提取所有曝光时间数据
        exposure_times = []
        for exif in self.exif_data_list:
            exposure_time = exif.get('曝光时间')

            if exposure_time:
                exposure_times.append(str(exposure_time).strip())

        if not exposure_times:
            messagebox.showinfo("信息", "没有找到曝光时间数据")
            return

        # 清除之前的图表
        for widget in self.shutter_chart_frame.winfo_children():
            widget.destroy()

        # 清除文本区域
        self.shutter_text.delete(1.0, tk.END)

        # 统计曝光时间
        counter = Counter(exposure_times)

        # 显示文本结果
        self.shutter_text.insert(tk.END, "快门速度统计（基于曝光时间）:\n")
        self.shutter_text.insert(tk.END, "=" * 40 + "\n")
        total = len(exposure_times)
        for exposure, count in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            self.shutter_text.insert(tk.END, f"{exposure}: {count} 张 ({percentage:.1f}%)\n")

        # 创建图表
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
        # 只显示前15个最常用的曝光时间
        sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:15]
        labels = [exposure for exposure, count in sorted_items]
        values = [count for exposure, count in sorted_items]

        ax.bar(labels, values, color=plt.cm.Pastel1(np.arange(len(labels))))
        ax.set_title('快门速度分布（基于曝光时间）')
        ax.set_ylabel('图片数量')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # 在Tkinter中显示图表
        canvas = FigureCanvasTkAgg(fig, self.shutter_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def analyze_aperture(self):
        """分析光圈统计 - 严格按照原始数值统计"""
        if not self.exif_data_list:
            messagebox.showwarning("警告", "请先加载图片")
            return

        # 提取所有光圈数据
        apertures = []
        for exif in self.exif_data_list:
            aperture = exif.get('光圈值')

            if aperture:
                # 直接使用原始字符串值，不进行转换
                apertures.append(str(aperture).strip())

        if not apertures:
            messagebox.showinfo("信息", "没有找到光圈数据")
            return

        # 清除之前的图表
        for widget in self.aperture_chart_frame.winfo_children():
            widget.destroy()

        # 清除文本区域
        self.aperture_text.delete(1.0, tk.END)

        # 统计光圈值
        counter = Counter(apertures)

        # 显示文本结果
        self.aperture_text.insert(tk.END, "光圈值统计（原始数值）:\n")
        self.aperture_text.insert(tk.END, "=" * 40 + "\n")
        total = len(apertures)
        for aperture, count in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            self.aperture_text.insert(tk.END, f"{aperture}: {count} 张 ({percentage:.1f}%)\n")

        # 创建图表
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
        # 只显示前15个最常用的光圈值
        sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:15]
        labels = [aperture for aperture, count in sorted_items]
        values = [count for aperture, count in sorted_items]

        ax.bar(labels, values, color=plt.cm.Pastel2(np.arange(len(labels))))
        ax.set_title('常用光圈值统计 (前15)')
        ax.set_ylabel('图片数量')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # 在Tkinter中显示图表
        canvas = FigureCanvasTkAgg(fig, self.aperture_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def analyze_iso(self):
        """分析ISO统计 - 严格按照原始数值统计"""
        if not self.exif_data_list:
            messagebox.showwarning("警告", "请先加载图片")
            return

        # 提取所有ISO数据
        iso_values = []
        for exif in self.exif_data_list:
            iso = exif.get('ISO')

            if iso:
                # 直接使用原始字符串值，不进行转换
                iso_values.append(str(iso).strip())

        if not iso_values:
            messagebox.showinfo("信息", "没有找到ISO数据")
            return

        # 清除之前的图表
        for widget in self.iso_chart_frame.winfo_children():
            widget.destroy()

        # 清除文本区域
        self.iso_text.delete(1.0, tk.END)

        # 统计ISO值
        counter = Counter(iso_values)

        # 显示文本结果
        self.iso_text.insert(tk.END, "ISO感光度统计（原始数值）:\n")
        self.iso_text.insert(tk.END, "=" * 40 + "\n")
        total = len(iso_values)
        for iso, count in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            self.iso_text.insert(tk.END, f"{iso}: {count} 张 ({percentage:.1f}%)\n")

        # 创建图表
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
        # 只显示前15个最常用的ISO值
        sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:15]
        labels = [iso for iso, count in sorted_items]
        values = [count for iso, count in sorted_items]

        ax.bar(labels, values, color=plt.cm.Set2(np.arange(len(labels))))
        ax.set_title('ISO感光度统计 (前15)')
        ax.set_ylabel('图片数量')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # 在Tkinter中显示图表
        canvas = FigureCanvasTkAgg(fig, self.iso_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def analyze_camera(self):
        """分析相机型号统计"""
        if not self.exif_data_list:
            messagebox.showwarning("警告", "请先加载图片")
            return

        # 提取所有相机型号数据
        cameras = []
        for exif in self.exif_data_list:
            camera = exif.get('相机型号')

            if camera:
                cameras.append(str(camera).strip())

        if not cameras:
            messagebox.showinfo("信息", "没有找到相机型号数据")
            return

        # 清除之前的图表
        for widget in self.camera_chart_frame.winfo_children():
            widget.destroy()

        # 清除文本区域
        self.camera_text.delete(1.0, tk.END)

        # 统计相机型号
        counter = Counter(cameras)

        # 显示文本结果
        self.camera_text.insert(tk.END, "相机型号统计:\n")
        self.camera_text.insert(tk.END, "=" * 40 + "\n")
        total = len(cameras)
        for camera, count in sorted(counter.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            self.camera_text.insert(tk.END, f"{camera}: {count} 张 ({percentage:.1f}%)\n")

        # 创建图表
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
        # 只显示前8个最常用的相机型号
        sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:8]
        labels = [camera for camera, count in sorted_items]
        values = [count for camera, count in sorted_items]

        ax.bar(labels, values, color=plt.cm.tab20c(np.arange(len(labels))))
        ax.set_title('相机型号使用统计 (前8)')
        ax.set_ylabel('图片数量')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # 在Tkinter中显示图表
        canvas = FigureCanvasTkAgg(fig, self.camera_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def analyze_datetime(self):
        """分析拍摄时间统计"""
        if not self.exif_data_list:
            messagebox.showwarning("警告", "请先加载图片")
            return

        # 提取所有拍摄时间数据
        datetimes = []
        for exif in self.exif_data_list:
            dt = exif.get('拍摄时间')

            if dt:
                try:
                    dt_str = str(dt)
                    # 尝试多种日期格式
                    formats = [
                        '%Y:%m:%d %H:%M:%S',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y/%m/%d %H:%M:%S',
                        '%Y.%m.%d %H:%M:%S'
                    ]

                    dt_obj = None
                    for fmt in formats:
                        try:
                            dt_obj = datetime.strptime(dt_str, fmt)
                            break
                        except:
                            continue

                    if dt_obj:
                        datetimes.append(dt_obj)
                except:
                    continue

        if not datetimes:
            messagebox.showinfo("信息", "没有找到拍摄时间数据")
            return

        # 清除之前的图表
        for widget in self.datetime_chart_frame.winfo_children():
            widget.destroy()

        # 清除文本区域
        self.datetime_text.delete(1.0, tk.END)

        # 根据分组方式处理数据
        group_type = self.datetime_group_var.get()

        if group_type == "year":
            # 按年分组
            years = [dt.year for dt in datetimes]
            counter = Counter(years)

            # 显示文本结果
            self.datetime_text.insert(tk.END, "拍摄年份统计:\n")
            self.datetime_text.insert(tk.END, "=" * 40 + "\n")
            total = len(datetimes)
            for year, count in sorted(counter.items()):
                percentage = (count / total) * 100
                self.datetime_text.insert(tk.END, f"{year}年: {count} 张 ({percentage:.1f}%)\n")

            # 创建图表
            fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
            labels = [f"{year}年" for year, count in sorted(counter.items())]
            values = [count for year, count in sorted(counter.items())]

            ax.bar(labels, values, color=plt.cm.viridis(np.linspace(0, 1, len(labels))))
            ax.set_title('拍摄年份分布')
            ax.set_ylabel('图片数量')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()

        elif group_type == "month":
            # 按月分组
            months = [dt.month for dt in datetimes]
            counter = Counter(months)

            # 显示文本结果
            self.datetime_text.insert(tk.END, "拍摄月份统计:\n")
            self.datetime_text.insert(tk.END, "=" * 40 + "\n")
            total = len(datetimes)
            month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                           '七月', '八月', '九月', '十月', '十一月', '十二月']
            for month in range(1, 13):
                count = counter.get(month, 0)
                if count > 0:
                    percentage = (count / total) * 100
                    self.datetime_text.insert(tk.END, f"{month_names[month - 1]}: {count} 张 ({percentage:.1f}%)\n")

            # 创建图表
            fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
            labels = [month_names[i] for i in range(12)]
            values = [counter.get(i + 1, 0) for i in range(12)]

            ax.bar(labels, values, color=plt.cm.spring(np.linspace(0, 1, 12)))
            ax.set_title('拍摄月份分布')
            ax.set_ylabel('图片数量')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()

        else:  # hour
            # 按小时分组
            hours = [dt.hour for dt in datetimes]
            counter = Counter(hours)

            # 显示文本结果
            self.datetime_text.insert(tk.END, "拍摄时间(小时)统计:\n")
            self.datetime_text.insert(tk.END, "=" * 40 + "\n")
            total = len(datetimes)
            for hour in range(24):
                count = counter.get(hour, 0)
                percentage = (count / total) * 100
                hour_str = f"{hour:02d}:00-{hour:02d}:59"
                self.datetime_text.insert(tk.END, f"{hour_str}: {count} 张 ({percentage:.1f}%)\n")

            # 创建图表
            fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
            labels = [f"{h:02d}:00" for h in range(24)]
            values = [counter.get(h, 0) for h in range(24)]

            ax.bar(labels, values, color=plt.cm.cool(np.linspace(0, 1, 24)))
            ax.set_title('拍摄时间(小时)分布')
            ax.set_ylabel('图片数量')
            ax.set_xlabel('小时')
            ax.tick_params(axis='x', rotation=90)
            plt.tight_layout()

        # 在Tkinter中显示图表
        canvas = FigureCanvasTkAgg(fig, self.datetime_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def parse_exif_value(self, value, as_int=False):
        """解析EXIF值，转换为浮点数或整数"""
        try:
            # 如果已经是数字类型，直接返回
            if isinstance(value, (int, float)):
                if as_int:
                    return int(value)
                else:
                    return float(value)

            # 转换为字符串
            value_str = str(value).strip()

            # 处理分数形式（如"1/125"）
            if '/' in value_str:
                parts = value_str.split('/')
                if len(parts) == 2:
                    try:
                        numerator = float(parts[0])
                        denominator = float(parts[1])
                        result = numerator / denominator
                        return int(result) if as_int else result
                    except:
                        pass

            # 处理可能带有单位的情况（如"50.0 mm"）
            # 提取数字部分
            match = re.search(r'([-+]?\d*\.?\d+)', value_str)
            if match:
                numeric_value = match.group(1)
                result = float(numeric_value)
                return int(result) if as_int else result

            # 如果上面都不行，尝试直接转换
            result = float(value_str)
            return int(result) if as_int else result

        except Exception as e:
            print(f"解析EXIF值 '{value}' 时出错: {e}")
            return None

    def display_image_with_exif(self, event=None):
        """显示图片和对应的EXIF数据"""
        if not self.exif_data_list:
            return

        # 获取选中的图片
        selected_idx = self.image_combo.current()
        if selected_idx == -1 and self.image_files:
            selected_idx = 0

        if selected_idx == -1:
            return

        # 更新当前图片索引
        self.current_image_index = selected_idx

        # 获取对应的EXIF数据
        exif_data = self.exif_data_list[selected_idx]
        image_path = exif_data.get('FilePath', '')

        if not image_path or not os.path.exists(image_path):
            return

        # 清除之前的图片
        self.image_canvas.delete("all")

        # 清除Treeview中的数据
        for item in self.exif_tree.get_children():
            self.exif_tree.delete(item)

        try:
            # 打开并调整图片大小以适应画布
            img = Image.open(image_path)

            # 获取画布尺寸
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()

            # 如果画布尺寸为1，使用默认尺寸
            if canvas_width <= 1:
                canvas_width = 400
            if canvas_height <= 1:
                canvas_height = 300

            # 计算缩放比例
            img_width, img_height = img.size
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            scale = min(width_ratio, height_ratio, 1)  # 限制最大缩放为1

            # 调整图片尺寸
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 转换为PhotoImage
            self.current_photo = ImageTk.PhotoImage(img_resized)

            # 在画布上居中显示图片
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=self.current_photo)

            # 显示图片信息
            info_text = f"图片 {selected_idx + 1}/{len(self.image_files)}: {os.path.basename(image_path)}"
            self.image_canvas.create_text(
                canvas_width // 2, 10,
                text=info_text,
                fill="white",
                font=("Arial", 10, "bold"),
                anchor=tk.N
            )

            # 更新状态
            self.status_var.set(f"正在显示图片: {os.path.basename(image_path)}")

            # 更新缩略图窗口中的选中状态
            if self.thumbnail_window and self.thumbnail_window.winfo_exists():
                self.update_thumbnail_selection()

        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            return

        # 显示EXIF数据到Treeview
        for key, value in exif_data.items():
            if key not in ['FileName', 'FilePath']:
                # 翻译标签名称
                tag_name = self.exif_translation.get(key, key)
                self.exif_tree.insert('', tk.END, values=(tag_name, str(value)))

    def export_all_data(self):
        """导出所有EXIF数据到JSON文件"""
        if not self.exif_data_list:
            messagebox.showwarning("警告", "没有可导出的数据")
            return

        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if not file_path:
            return

        try:
            # 准备导出的数据
            export_data = {
                'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_images': len(self.image_files),
                'images_with_exif': len(self.exif_data_list),
                'exif_data': self.exif_data_list
            }

            # 写入JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

            messagebox.showinfo("导出成功", f"数据已成功导出到:\n{file_path}")
            self.status_var.set(f"数据已导出到: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("导出失败", f"导出数据时出错:\n{str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = ImageExifAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()