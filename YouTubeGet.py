import os
import subprocess

import browsercookie
import yt_dlp
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 配置参数
yt_dlp_path = 'D:/yt-dlp/yt-dlp.exe'
cookies_path = 'D://pycharmWorkspace//youtube//cookies.txt'
proxy = 'socks5://127.0.0.1:10808'
download_path = 'downloads/'

# 更新 cookies 文件的函数
def update_cookies():
    cookies = browsercookie.firefox()
    with open(cookies_path, "w") as file:
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
                http_only = "TRUE"  # Assume HttpOnly as True
                name = cookie.name
                value = cookie.value
                if name and value:
                    file.write(f"{domain}\t{http_only}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")


# 下载进度回调函数
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        filename = d.get('filename', 'Unknown')
        session['progress'] = {'filename': filename, 'percent': percent}
    elif d['status'] == 'finished':
        session['progress'] = {'filename': d.get('filename', 'Unknown'), 'percent': 100}


# 下载视频的函数
def download_video(video_url):
    update_cookies()

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': download_path + '%(title)s.%(ext)s',
        'proxy': proxy,
        'cookies': cookies_path,
        'progress_hooks': [progress_hook],
        'noplaylist': True,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])







# 路由：首页
@app.route('/')
def index():
    return render_template('index.html')


# 路由：下载视频
@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    if not video_url:
        return jsonify({'error': '请输入视频链接！'})

    # 启动下载视频
    download_video(video_url)

    return jsonify({'status': '下载开始'})


# 路由：获取下载进度
@app.route('/progress', methods=['GET'])
def progress():
    progress_data = session.get('progress', {'filename': '', 'percent': 0})
    return jsonify(progress_data)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
