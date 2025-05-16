import os
import re
import logging
import sys
import time
import yt_dlp
import argparse

# 设置控制台输出编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subtitle_download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def sanitize_filename(title):
    """清理文件名中的非法字符"""
    # 移除非法字符
    sanitized = re.sub(r'[\\/*?:"<>|]', "", title)
    # 移除其他潜在问题字符
    sanitized = re.sub(r'[^\w\s\-\.]', "", sanitized)
    # 移除空格前后的点和空格
    sanitized = sanitized.strip('. ')
    # 限制文件名长度，更保守一些
    return sanitized[:80]

def extract_clean_text(vtt_content):
    """从VTT格式中提取纯文本"""
    lines = vtt_content.split('\n')
    clean_text = []
    last_line = None
    
    for line in lines:
        # 跳过VTT头部信息和空行
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:') or not line.strip():
            continue
        # 跳过时间戳行
        if '-->' in line:
            continue
        # 跳过空行
        if not line.strip():
            continue
        # 移除HTML标签和特殊字符
        clean_line = re.sub(r'<[^>]+>', '', line)
        clean_line = re.sub(r'align:start position:\d+%', '', clean_line)
        clean_line = clean_line.strip()
        
        # 跳过重复的行
        if clean_line and clean_line != last_line:
            clean_text.append(clean_line)
            last_line = clean_line
    
    return '\n'.join(clean_text)

def download_video_content(video_url, output_dir, video_index=0, max_retries=3):
    """下载视频内容（描述和纯文本脚本）"""
    for attempt in range(max_retries):
        try:
            ydl_opts = {
                'skip_download': True,  # 不下载视频
                'writesubtitles': True,  # 下载字幕
                'writeautomaticsub': True,  # 下载自动生成的字幕
                'subtitleslangs': ['en'],  # 下载英文字幕
                'outtmpl': '%(title)s.%(ext)s',  # 输出模板
                'quiet': True,
                'no_warnings': True,
                'writeinfojson': False,  # 不保存视频元数据信息
            }
            
            # 获取视频信息
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    raise Exception("无法获取视频信息")
                
                title = info.get('title', 'Unknown Title')
                description = info.get('description', '')
                logging.info(f"正在处理视频: {title}")
                
                # 清理标题作为文件夹名
                folder_name = sanitize_filename(title)
                folder_path = os.path.join(output_dir, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                # 删除可能存在的旧文件
                old_description_path = os.path.join(folder_path, f"{folder_name}_description.txt")
                old_script_path = os.path.join(folder_path, f"{folder_name}_script.txt")
                
                if os.path.exists(old_description_path):
                    try:
                        os.remove(old_description_path)
                    except Exception as e:
                        logging.warning(f"删除旧描述文件失败: {str(e)}")
                
                if os.path.exists(old_script_path):
                    try:
                        os.remove(old_script_path)
                    except Exception as e:
                        logging.warning(f"删除旧脚本文件失败: {str(e)}")
                
                # 保存视频描述
                description_path = os.path.join(folder_path, "视频描述.txt")
                try:
                    with open(description_path, 'w', encoding='utf-8') as f:
                        f.write(description)
                except Exception as e:
                    logging.warning(f"保存视频描述文件失败: {str(e)}")
                    # 尝试使用更短的文件路径
                    try:
                        short_path = os.path.join(output_dir, f"video_{video_index}")
                        os.makedirs(short_path, exist_ok=True)
                        with open(os.path.join(short_path, "描述.txt"), 'w', encoding='utf-8') as f:
                            f.write(description)
                        folder_path = short_path  # 更新文件夹路径
                    except Exception as e2:
                        logging.error(f"创建备用路径也失败: {str(e2)}")
                        return False
                
                # 更新输出模板
                ydl_opts.update({
                    'outtmpl': os.path.join(folder_path, folder_name),
                })
                
                # 下载自动生成的字幕
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # 处理字幕文件
                vtt_files = [f for f in os.listdir(folder_path) if f.endswith('.vtt')]
                if vtt_files:
                    vtt_path = os.path.join(folder_path, vtt_files[0])
                    with open(vtt_path, 'r', encoding='utf-8') as f:
                        vtt_content = f.read()
                    
                    # 提取纯文本
                    clean_text = extract_clean_text(vtt_content)
                    
                    # 保存纯文本脚本
                    script_path = os.path.join(folder_path, "原文.txt")
                    try:
                        with open(script_path, 'w', encoding='utf-8') as f:
                            f.write(clean_text)
                    except Exception as e:
                        logging.warning(f"保存脚本文件失败: {str(e)}")
                        try:
                            # 使用更短的文件名
                            with open(os.path.join(folder_path, "文本.txt"), 'w', encoding='utf-8') as f:
                                f.write(clean_text)
                        except Exception as e2:
                            logging.error(f"使用短文件名保存脚本仍然失败: {str(e2)}")
                            return False
                    
                    # 删除原始的VTT文件
                    os.remove(vtt_path)
                    
                    # 删除可能存在的JSON文件
                    json_file = os.path.join(folder_path, f"{folder_name}.info.json")
                    if os.path.exists(json_file):
                        os.remove(json_file)
                    
                    logging.info(f"成功提取纯文本脚本并保存到: {folder_path}")
                    
                    # 输出处理完成的信息
                    print(f"✓ 视频 '{title}' 已完成下载")
                    
                    return True
                else:
                    logging.warning(f"未找到字幕文件: {title}")
                    return False
                
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                logging.warning(f"发生错误: {str(e)}，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logging.error(f"处理视频时出错 {video_url}: {str(e)}")
    
    return False

def process_links_file(file_path):
    """处理包含视频链接的文件"""
    # 创建输出目录
    output_dir = "subtitles"
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取链接文件
    with open(file_path, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]
    
    # 处理每个链接
    success_count = 0
    for i, link in enumerate(links, 1):
        print(f"处理第 {i}/{len(links)} 个视频: {link}")
        if download_video_content(link, output_dir, i):
            success_count += 1
        time.sleep(2)  # 添加间隔，避免请求过于频繁
    
    logging.info(f"处理完成。成功下载 {success_count}/{len(links)} 个视频的内容")
    
    print("\n============================================================")
    print(f"全部处理完成! 共处理 {len(links)} 个链接，成功 {success_count} 个")
    print("所有文件已保存在 subtitles 文件夹中")
    print("每个视频文件夹包含:")
    print("  - 视频描述.txt (原始视频描述)")
    print("  - 原文.txt (提取的字幕文本)")
    print("============================================================")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='下载YouTube视频的字幕和描述')
    parser.add_argument('file', nargs='?', help='包含YouTube链接的文本文件路径')
    args = parser.parse_args()
    
    if args.file:
        file_path = args.file
    else:
        # 如果没有提供文件路径，显示使用说明
        logging.info("请提供包含YouTube链接的文本文件路径")
        logging.info("用法: python youtube_subtitle_downloader.py [文件路径]")
        logging.info("例如: python youtube_subtitle_downloader.py youtube_links.txt")
        return
    
    if os.path.exists(file_path):
        logging.info(f"开始处理文件: {file_path}")
        process_links_file(file_path)
    else:
        logging.error(f"找不到文件: {file_path}")
        logging.info("请确认文件路径是否正确")

if __name__ == "__main__":
    main() 