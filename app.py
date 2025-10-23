from flask import Flask, request, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

# Folder to store downloaded files
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({
        "status": True,
        "message": "Welcome to AutoDL API (Render Version)",
        "usage": "/download?url=VIDEO_URL"
    })


@app.route("/download", methods=["GET"])
def download_video():
    url = request.args.get("url")

    if not url:
        return jsonify({
            "status": False,
            "message": "Missing ?url= parameter"
        })

    try:
        file_id = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        title = info.get("title", "Unknown Title")
        duration = info.get("duration", 0)
        uploader = info.get("uploader", "Unknown")
        webpage_url = info.get("webpage_url", url)

        downloaded_file = None
        for ext in ["mp4", "mkv", "webm"]:
            path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.{ext}")
            if os.path.exists(path):
                downloaded_file = path
                break

        return jsonify({
            "status": True,
            "message": "Download successful!",
            "title": title,
            "duration": duration,
            "uploader": uploader,
            "video_url": webpage_url,
            "file_path": downloaded_file
        })

    except Exception as e:
        return jsonify({
            "status": False,
            "message": f"Error: {str(e)}"
        })


if __name__ == "__main__":
    # Render automatically sets the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
