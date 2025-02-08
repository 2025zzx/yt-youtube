from flask import Flask, render_template, request, jsonify, session
import os
import yt_dlp
import threading
import json
import browsercookie

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 配置路径
downloads_video_path = "downloads/video"

# 配置项
common_opts = {
    'format': 'bestvideo+bestaudio/best',
    'proxy': 'http://127.0.0.1:10809',
    'cookiefile': r'cookies.txt',
    'noplaylist': True,
    'merge_output_format': 'mp4',
    'quiet': False,
    'no_warnings': False,
    'verbose': True,
    'socket_timeout': 30,
    'retries': 3,
    'nocheckcertificate': True,
    'prefer_insecure': True,
    'concurrent_fragment_downloads': 1,
}

# yt-dlp 基础配置
common_opts2 = {
    'cookiefile': r'cookies.txt',
    'quiet': False,
    'no_warnings': False,
    'verbose': True,
    'proxy': 'http://127.0.0.1:10809',
    'socket_timeout': 30,
    'retries': 3,
    'nocheckcertificate': True,
    'prefer_insecure': True
}

# 存储下载进度的全局字典，使用 URL 作为唯一标识
download_progress_data = {}

# 更新 cookies 文件的函数
def update_cookies():
    cookies = browsercookie.firefox()
    with open('cookies.txt', "w") as file:
        file.write("# Netscape HTTP Cookie File\n")
        file.write("# http://curl.haxx.se/rfc/cookie_spec.html\n")
        file.write("# This is a generated file!  Do not edit.\n\n")
        for cookie in cookies:
            if "youtube.com" in cookie.domain:
                domain = cookie.domain
                if not domain.startswith('.'):
                    domain = '.' + domain
                path = cookie.path if cookie.path else "/"
                secure = "TRUE" if cookie.secure else "FALSE"
                expires = str(cookie.expires) if cookie.expires else "0"
                http_only = "TRUE"
                name = cookie.name
                value = cookie.value
                if name and value:
                    file.write(f"{domain}\t{http_only}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")


# 下载进度回调，使用 URL 作为任务的唯一标识
def download_progress(d, progress_callback, video_url):
    # 仅使用数字部分的进度，避免出现多余的 "%"
    percent = d['_percent_str']
    percent = float(percent.replace('%', ''))  # 获取百分比数字部分
    download_progress_data[video_url] = {'filename': d['filename'], 'percent': percent}  # 存储进度数据
    progress_callback(video_url, d['filename'], percent)  # 传递视频 URL 和进度


# 下载视频的函数
def download_video(url, progress_callback):
    update_cookies()
    video_opts = {
        **common_opts,
        'outtmpl': str(downloads_video_path + '/%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress_hooks': [lambda d: download_progress(d, progress_callback, url)]  # 添加进度回调
    }
    with yt_dlp.YoutubeDL(video_opts) as ydl:
        ydl.download([url])

# 用于后台执行下载任务
def run_download(video_url, progress_callback):
    thread = threading.Thread(target=download_video, args=(video_url, progress_callback))
    thread.start()

# 获取视频信息
@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    with yt_dlp.YoutubeDL(common_opts2) as ydl:
        info = ydl.extract_info(url, download=False)
        video_info = {
            'title': info['title'],
            'duration': f"{info['duration'] // 60}:{info['duration'] % 60:02d}",
            'thumbnail': info['thumbnail'],
            'url': url
        }

    return jsonify({'status': 'success', 'video_info': video_info})

# 路由：首页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：下载视频
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()  # 获取请求中的 JSON 数据
    video_url = data.get('url')  # 从 JSON 数据中获取视频链接
    if not video_url:
        return jsonify({'error': '请输入视频链接！'})

    def progress_callback(video_url, filename, percent):
        print(json.dumps({'video_url': video_url, 'filename': filename, 'percent': percent}))

    run_download(video_url, progress_callback)
    return jsonify({'status': '下载开始'})

# 路由：获取下载进度
@app.route('/progress', methods=['POST'])
def progress():
    data = request.get_json()
    video_url = data.get('url')  # 从请求中获取视频链接
    if video_url in download_progress_data:
        return jsonify(download_progress_data[video_url])
    return jsonify({'error': '未找到该视频的下载进度'})

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
