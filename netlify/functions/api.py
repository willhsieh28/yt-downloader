import json
import logging
import sys
import subprocess

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # Only allow POST requests
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

    try:
        # 嘗試 import yt_dlp，如果失敗代表環境沒有安裝
        import yt_dlp
    except ImportError:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Server Configuration Error: yt-dlp module not found. Please deploy via Git to install dependencies.'})
        }

    try:
        body = json.loads(event['body'])
        url = body.get('url')
        
        if not url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'URL is required'})
            }

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            # 必須防止 yt-dlp 嘗試下載，我們只要資訊
            'extract_flat': 'in_playlist', 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 使用 extract_info 但不下載
            info = ydl.extract_info(url, download=False)
            
            # Extract relevant info
            video_url = info.get('url')
            title = info.get('title')
            thumbnail = info.get('thumbnail')
            duration = info.get('duration_string')
            uploader = info.get('uploader')
            
            if not video_url:
                 return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Could not resolve video URL (DRM or extraction failed)'})
                }

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                     'Access-Control-Allow-Origin': '*' 
                },
                'body': json.dumps({
                    'title': title,
                    'url': video_url,
                    'thumbnail': thumbnail,
                    'duration': duration,
                    'uploader': uploader
                })
            }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Processing Error: {str(e)}"})
        }
