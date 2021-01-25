import flask
import os
from flask import request, abort
import hmac
import hashlib
import json
import requests
import shutil
import subprocess

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
    bot_process = subprocess.Popen("./latest/src/main.py")


def get_latest():
    r = requests.get(repo_url + "/releases/latest").json()
    base_url = r["url"]
    if r["tag_name"] in os.listdir() and bot_process is not None:
        return

    elif r["tag_name"] in os.listdir:
        os.symlink(f'./{r["tag_name"]}', './latest')
        start_latest()

    assets = request.get(base_url + "/assets").json()
    asset = [asset for asset in assets if asset["name"] == "source.zip"][0]
    zipped_src_file_fp = download_file(asset["browser_download_url"])
    shutil.unpack_archive(zipped_src_file_fp, zipped_src_file_fp[r["tag_name"]])
    os.symlink(f'./{r["tag_name"]}', './latest')


@app.route('/update', methods=["POST"])
def update():
    assert request.method == "POST"
    signature = request.headers.get("X-Hub-Signature")
    if not signature or not signature.startswith('sha1='):
        logs.write(f'{request.remote_addr} sent a request without a valid signature\n')
        abort(400, "Signature required")

    digest = hmac.new(github_secret.encode(), request.data, hashlib.sha1).hexdigest()

    if not hmac.compare_digest(signature, "sha1=" + digest):
        logs.write(f'{request.remote_addr} sent a request with an invalid signature\n')
        abort(400, "Invalid signature")


if __name__ == '__main__':
    start_latest()
