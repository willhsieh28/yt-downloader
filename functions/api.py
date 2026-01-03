import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 為了防止冷啟動超時，我們盡量減少 global imports
# import yt_dlp (移到 handler 內)

def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {'statusCode': 405, 'body': 'Method Not Allowed'}

    try:
        import yt_dlp
    except ImportError:
         return {
            'statusCode': 500,
            'body': json.dumps({'error': 'yt-dlp not installed'})
        }

    try:
        body = json.loads(event['body'])
        url = body.get('url')
        
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'dump_single_json': True, # Key change: lighter execution
            'extract_flat': True,     # Key change: do not extract details yet
        }
        
        # 第一次輕量請求，只拿基本資訊，避免超時
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 這裡回傳最基礎的資訊
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'url': info.get('url') or url, # 有時 flat extract 拿不到直連
                    'duration': info.get('duration_string'),
                    'uploader': info.get('uploader')
                })
            }

    except Exception as e:
        logger.error(str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
