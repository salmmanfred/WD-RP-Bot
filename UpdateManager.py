import flask
import os
from flask import request, abort
import hmac
import hashlib
import json
import requests
import shutil
import subprocess
from gevent.pywsgi import WSGIServer

bot_process = None
app = flask.Flask(__name__)
github_secret = json.load(open('./config.json', "r"))["github_secret"]
repo_url = "https://api.github.com/repos/gamingdiamond982/WD-RP-Bot"
logs = open('./logs.txt', 'a')


def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def start_latest():
    global bot_process
    get_latest()
    fp = "./latest/src/main.py"
    bot_process = subprocess.Popen(["/usr/bin/python3", fp])


def get_latest():
    r = requests.get(repo_url + "/releases/latest").json()

    def link():
        try:
            os.unlink('./latest')
        except FileNotFoundError:
            pass
        os.symlink(f'./{r["tag_name"]}/WD-RP-Bot-{r["tag_name"]}/', './latest')

    if r["tag_name"] in os.listdir() and bot_process is not None:
        return

    elif r["tag_name"] in os.listdir():
        link()

    if bot_process is not None:
        bot_process.kill()

    zipped_src_file_fp = download_file(f"https://github.com/gamingdiamond982/WD-RP-Bot/archive/{r['tag_name']}.zip")
    shutil.unpack_archive(zipped_src_file_fp, f'./{r["tag_name"]}')
    os.remove(f'./{r["tag_name"]}.zip')
    link()


@app.route('/update', methods=["POST"])
def update():
    assert request.method == "POST"
    req_data = request.get_data()
    x_hub_sig = request.headers.get("X-Hub-Signature").split('=')[1]
    print("Got x_hub_sig: " + x_hub_sig)
    print("Generating sig from\n\tgithub_secret: " + github_secret)
    print("\trequest.data: " + str(req_data) + "\n\n\n")
    signature = hmac.new(github_secret.encode('utf-8'), req_data, hashlib.sha1).hexdigest()
    print("Trying: " + signature + " ; " + x_hub_sig)
    if not hmac.compare_digest(signature, x_hub_sig):
        abort(401, "Unauthorised")

    start_latest()

    return {"code": 200}


if __name__ == '__main__':
    start_latest()
    WSGIServer(('', 5000), app)
