# YouTube字幕下载工具

这是一个简单的工具，用于下载YouTube视频的字幕和描述，并保存为纯文本格式。

## 功能特点

- 自动读取指定的视频链接文件
- 自动创建以视频标题命名的文件夹
- 下载视频描述和字幕
- 自动提取纯文本内容
- 自动记录处理日志
- 支持批量处理多个视频

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 准备视频链接：
   - 在`youtube视频链接`文件夹中创建txt文件（如`0504.txt`）
   - 每行一个YouTube视频链接

3. 运行程序：
```bash
python youtube_subtitle_downloader.py youtube视频链接/0504.txt
```

或者使用批处理文件：
```bash
download_subtitles.bat youtube视频链接/0504.txt
```

## 文件结构

- `youtube_subtitle_downloader.py`: 主程序脚本
- `download_subtitles.bat`: 便捷的批处理启动文件
- `requirements.txt`: 依赖文件
- `youtube视频链接/`: 存放视频链接的文件夹
- `subtitles/`: 存放下载的内容
  - 每个视频会创建独立文件夹
  - 包含`视频描述.txt`和`原文.txt`文件
- `subtitle_download.log`: 日志文件

## 处理结果

程序执行后，会在`subtitles`文件夹中为每个视频创建一个独立的文件夹，包含：
- `视频描述.txt`: 原始视频描述
- `原文.txt`: 提取的字幕文本

## 注意事项

- 确保网络连接正常
- 视频必须包含字幕（自动生成的也可以）
- 文件名会自动清理非法字符
- 处理结果会记录在日志文件中 