# 图片信息收集（Photo EXIF Stats）

> 批量读取一个文件夹里所有照片的 EXIF，统计**焦距 / 快门 / 光圈 / ISO / 相机型号 / 拍摄时间**六个维度的分布，每个维度配柱状图，并能把全部原始数据导出成 JSON。
>
> 一句话用途：**看清自己到底习惯用哪支镜头、哪档光圈、哪个时段按快门。**

![平台](https://img.shields.io/badge/platform-Windows%2010%2F11%20x64-blue)
![语言](https://img.shields.io/badge/python-3.10--3.12-green)
![GUI](https://img.shields.io/badge/GUI-tkinter%20%2B%20matplotlib-informational)
![许可](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 快速开始

1. 下载 `dist/图片信息收集.exe`，双击运行（免安装，免 Python）；
2. 点「选择文件夹」→ 选一个装着照片的目录（会**递归扫描子文件夹**）；
3. 点「加载图片」，等进度跑完；
4. 切到各个标签页，点右侧的「统计…」按钮出结果 + 柱状图；
5. 想看单张明细：切到「原始EXIF数据」，用 `←` `→` 翻图。

**完整的新手教程（含分桶边界、等效焦距陷阱、16 条常见问题）请看 👉 [操作说明.md](操作说明.md)**

想先试效果？用 `examples/sample-photos/` 里那 6 张示例照片，参数已写好，直接选它当图片文件夹即可。

---

## 七个标签页

| 标签页 | 统计内容 | 图表 |
|---|---|---|
| **焦距统计** | 按「范围」分 6 档，或按「具体值」取整计数 | 柱状图（具体值取前 15） |
| **快门速度统计** | 按曝光时间原始值计数（如 `1/125`） | 柱状图（前 15） |
| **光圈统计** | 按光圈原始值计数（如 `f/2.8`） | 柱状图（前 15） |
| **ISO统计** | 按 ISO 原始值计数 | 柱状图（前 15） |
| **相机型号统计** | 按机身型号计数 | 柱状图（前 8） |
| **拍摄时间统计** | 按年 / 按月 / 按小时分布 | 柱状图 |
| **原始EXIF数据** | 左侧图片预览 + 右侧全部 EXIF 明细（中文翻译） | — |

## 焦距分档规则

| 档位 | 判定 |
|---|---|
| 超广角 | < 20mm |
| 广角 | 20 ≤ f < 35 |
| 标准 | 35 ≤ f < 70 |
| 中长焦 | 70 ≤ f < 135 |
| 长焦 | 135 ≤ f < 300 |
| 超长焦 | ≥ 300mm |

> ⚠️ 统计用的是 **EXIF 里的实际焦距**，不是 35mm 等效焦距。APS-C 机身 18mm 会算进「超广角」，而它的等效视野其实是 27mm 的广角。详见操作说明第 10 节。

## 支持格式

`.jpg` `.jpeg` `.png` `.tiff` `.bmp` `.gif` `.cr3` `.cr2` `.nef` `.arw` `.dng`

> `.png` / `.gif` / `.bmp` 基本没有 EXIF；手机截图、微信传输图通常也被抹掉了参数。没有 EXIF 的图会加载但不出数据。

## 目录结构

```
.
├── reminder_app.py         # 全部源码（单文件，约 1760 行）
├── 图片信息收集.spec        # PyInstaller 打包配置（datas=[]）
├── package.bat             # 一键打包脚本
├── dist/图片信息收集.exe    # 已打包的 Windows 可执行文件
├── examples/
│   └── sample-photos/      # 6 张虚构参数的示例照片，可立即试跑
├── 操作说明.md              # 面向零基础使用者的详细说明书
└── .gitignore
```

## 导出 JSON

「原始EXIF数据」标签页右上角的「导出所有数据」会把当前已加载的全部记录写成 JSON：

```json
{
  "export_time": "2026-11-14 11:45:00",
  "total_images": 120,
  "images_with_exif": 118,
  "exif_data": [
    { "焦距": "85", "光圈值": "f/1.2", "ISO": "400",
      "相机型号": "Canon EOS R6", "镜头型号": "RF85mm F1.2 L USM",
      "FileName": "IMG_1003.jpg", "FilePath": "D:\\photos\\IMG_1003.jpg" }
  ]
}
```

## 自行打包

```bat
pip install pillow matplotlib numpy exifread rawpy pyinstaller
pyinstaller --clean --noconfirm 图片信息收集.spec
```

或直接跑源码：`python reminder_app.py`

## 本次修复说明（相对作者原始版本）

| 问题 | 现象 | 修复 |
|---|---|---|
| 镜头型号覆盖机身型号 | 「相机型号统计」里显示的全是镜头名（如 `RF85mm F1.2 L USM`） | 把 `LensModel` 的判断提到 `Model` 之前 |
| 35mm 等效焦距覆盖实际焦距 | 「焦距统计」可能用到等效焦距，导致分档偏移 | `FocalLengthIn35mmFilm` 单独存为「等效焦距」，不再覆盖「焦距」 |
| 修改时间覆盖拍摄时间 | 「拍摄时间统计」可能用的是文件修改时间 | `DateTimeOriginal` 优先，`DateTime` 仅在缺失时兜底 |

其余逻辑与原版保持一致。

## 已知限制

- 不含 EXIF 的图片会导致下拉框序号与数据错位（建议一个文件夹只放同批有 EXIF 的照片）
- CR3 / NEF / ARW 等 RAW 无法预览（PIL 打不开），只能取 EXIF
- 统计按「原始字符串」精确匹配，同一档光圈写成 `f/2.8` 和 `2.8` 会被算成两类
- 加载是同步的，大文件夹会卡住几十秒
- 仅支持 Windows

## License

MIT
