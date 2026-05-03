import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALLOWED_PROTOCOLS = {"http", "https"}


def _json_response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }


def _pick_direct_download_format(info):
    formats = info.get("formats") or []
    progressive_formats = []

    for fmt in formats:
        if not fmt.get("url"):
            continue
        if fmt.get("vcodec") == "none" or fmt.get("acodec") == "none":
            continue
        if fmt.get("protocol") not in ALLOWED_PROTOCOLS:
            continue

        progressive_formats.append(fmt)

    if not progressive_formats:
        return None

    def format_rank(fmt):
        return (
            1 if fmt.get("ext") == "mp4" else 0,
            fmt.get("height") or 0,
            fmt.get("tbr") or 0,
        )

    progressive_formats.sort(key=format_rank, reverse=True)
    return progressive_formats[0]


def _format_label(fmt):
    height = fmt.get("height")
    ext = fmt.get("ext") or "unknown"
    if height:
        return f"{height}p ({ext})"
    return ext

def handler(event, context):
    if event["httpMethod"] != "POST":
        return _json_response(405, {"error": "Method Not Allowed"})

    try:
        import yt_dlp
    except ImportError:
        return _json_response(500, {"error": "yt-dlp not installed"})

    try:
        body = json.loads(event.get("body") or "{}")
        url = (body.get("url") or "").strip()

        if not url:
            return _json_response(400, {"error": "Missing required field: url"})

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info.get("_type") == "playlist":
                return _json_response(
                    400,
                    {"error": "Playlist URLs are not supported yet. Please provide a single video URL."},
                )

            download_format = _pick_direct_download_format(info)
            if not download_format:
                return _json_response(
                    422,
                    {
                        "error": (
                            "No direct audio+video download format is available for this video. "
                            "The current serverless flow cannot safely merge separate streams yet."
                        )
                    },
                )

            return _json_response(
                200,
                {
                    "title": info.get("title"),
                    "thumbnail": info.get("thumbnail"),
                    "duration": info.get("duration_string"),
                    "uploader": info.get("uploader"),
                    "webpage_url": info.get("webpage_url") or url,
                    "download": {
                        "url": download_format.get("url"),
                        "format_id": download_format.get("format_id"),
                        "ext": download_format.get("ext"),
                        "quality": _format_label(download_format),
                        "filesize": download_format.get("filesize"),
                        "protocol": download_format.get("protocol"),
                    },
                    "warning": (
                        "Direct media URLs can expire and may be restricted by upstream providers. "
                        "If the download fails later, refresh the video information and try again."
                    ),
                },
            )

    except Exception as e:
        logger.error(str(e))
        return _json_response(500, {"error": str(e)})
