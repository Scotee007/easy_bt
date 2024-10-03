from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
import bencodepy

app = Flask(__name__)
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.debug = True


# 替代的 bt2magnet 函数
def bt2magnet(torrent_path):
    # 读取并解析 .torrent 文件
    with open(torrent_path, 'rb') as f:
        torrent_data = bencodepy.decode(f.read())

    # 获取 'info' 字段并进行哈希处理
    info = bencodepy.encode(torrent_data[b'info'])
    info_hash = hashlib.sha1(info).hexdigest()

    # 生成磁力链接
    return f"magnet:?xt=urn:btih:{info_hash}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=["POST"])
def upload():
    if request.method == "POST":
        files = request.files.getlist('file')  # 获取上传的多个文件
        magnet_links = []
        for f in files:
            if f:
                dir = os.path.join(app.config["UP_DIR"], secure_filename(f.filename))
                if not os.path.exists(app.config["UP_DIR"]):
                    os.makedirs(app.config["UP_DIR"])
                f.save(dir)
                magnet = bt2magnet(dir)
                magnet_links.append(magnet)
        return jsonify(result=magnet_links, status=1)
    return jsonify(result="转换失败", status=0)


if __name__ == '__main__':
    app.run(debug=True)
