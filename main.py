from flask import (
    Response,
    jsonify,
    Flask,
    send_file,
    request,
    render_template,
    send_from_directory,
)
from downloader import Downloader
from demucs_processor import DemucsProcessor
from spotify_to_yt import ConvertSpofity
import os
import glob

app = Flask(__name__)
global filename

# downloader = Downloader()
demucs_processor = DemucsProcessor()
downloader = Downloader()


@app.route("/", methods=["POST", "GET"])
def home():
    refresh_directories()
    return render_template("index.html")


import os
import shutil
import glob


@app.route("/delete", methods=["POST", "GET"])
def delete():
    # clear the contents of /tracks/htdemucs/ and /tracks/htdemucs_6s/

    return render_template("index.html")


@app.route("/download_video", methods=["POST"])
def download_audio():
    if request.method == "POST":
        input_url = request.json.get("url")
        if "spotify" in input_url:
            url = ConvertSpofity(input_url).get_youtube_url()
        else:
            url = input_url
        filetype = request.json.get("filetype")
        if url:
            filename = downloader.download_video(url, filetype)
            print("filename", filename)
    return jsonify({"status": "success", "filename": str(filename)})


def progress_check(d):
    if d["status"] == "finished":
        print("RUN DEMUCS")


@app.route("/process_audio", methods=["POST"])
def process_audio():
    filename = request.json.get("filename")
    filetype = request.json.get("filetype")
    num_stems = request.json.get("numStems")
    demucs_processor.process_audio(filename, filetype, num_stems)
    return jsonify({"message": "Finished", "filename": str(filename)})


@app.route("/download", methods=["POST", "GET"])
def download():
    filename = request.args.get("filename")
    response = send_file(f"{filename}.zip", as_attachment=True)

    # Delete the .zip file after sending it
    if os.path.exists(f"{filename}.zip"):
        os.remove(f"{filename}.zip")

    # Delete any .mp3 or .wav files
    for file in glob.glob("*.mp3"):
        os.remove(file)
    for file in glob.glob("*.wav"):
        os.remove(file)
    for file in glob.glob("*flac"):
        os.remove(file)

    return response


@app.route("/tracks/<stem_type>/<path:songname>", methods=["GET"])
def serve_audio(stem_type, songname):
    print("stem type", stem_type)
    print("songname", songname)
    directory = f"tracks/{stem_type}/{songname}"

    files = os.listdir(directory)
    return jsonify(files)


@app.route("/tracks/<stem_type>/<path:songname>/<filename>", methods=["GET"])
def serve_file(stem_type, songname, filename):
    return send_from_directory(f"tracks/{stem_type}/{songname}", filename)


# login page
@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")


# register page
@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")


def refresh_directories():
    for directory in glob.glob("tracks/htdemucs/*"):
        if os.path.isdir(directory):
            shutil.rmtree(directory)
    for directory in glob.glob("tracks/htdemucs_6s/*"):
        if os.path.isdir(directory):
            shutil.rmtree(directory)


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
