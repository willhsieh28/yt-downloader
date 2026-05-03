# yt-downloader

一個以 Netlify Functions 為後端、靜態前端為介面的輕量 YouTube 影片分析與下載入口原型。

This is a lightweight YouTube video analyzer and download-entry prototype powered by a static frontend and Netlify Functions.

目前這個專案的主要流程是：使用者貼上 YouTube 網址，前端把網址送到 Netlify Function，由 `yt-dlp` 擷取影片資訊與可直接使用的候選格式，再挑出一個較可靠的音訊加視訊合併格式，最後把標題、縮圖、頻道、時長與下載連結顯示在頁面上。

## 目前狀態 Current Status

這個 repository 已經有可運作的雛形，但仍偏向 prototype，而不是完整產品。

This repository is functional as a prototype, but it should not yet be treated as a finished production-ready downloader.

目前已知狀況如下：

- 後端現在會主動挑選可直接使用的 audio+video 合併格式，可靠度比原本只回傳原始網址高。
- 仍然不是完整的 server-side downloader，某些影片可能沒有適合直接下載的 progressive format。
- 部署設定目前仍不完整。
- 專案尚未有自動化測試。

## 功能 Features

- 單頁式前端，可貼上 YouTube 影片網址
- 基本的 loading 與錯誤提示狀態
- 以 Netlify Functions 提供 serverless 後端
- 使用 `yt-dlp` 擷取影片資訊與可用格式
- 後端優先挑選可直接下載的 audio+video 合併格式
- 前端顯示選中的畫質資訊與下載按鈕

## 運作方式 How It Works

1. 使用者開啟 `public/` 內的前端頁面。
2. 表單把貼上的網址送到 `/.netlify/functions/api`。
3. Netlify Function 呼叫 `yt-dlp`，讀取影片資訊與格式列表。
4. Function 從格式列表中挑選較可靠的直接下載格式並回傳 JSON。
5. 前端把結果渲染成卡片。

更完整的流程說明可參考 [docs/architecture.md](D:/project/Codex/改作業專案/repo_read/docs/architecture.md)。

## 專案結構 Project Structure

```text
.
|-- functions/
|   `-- api.py                 # Netlify Function handler
|-- public/
|   |-- index.html             # 前端 HTML
|   |-- app.js                 # 前端互動邏輯
|   `-- style.css              # 前端樣式
|-- docs/
|   |-- architecture.md        # 架構說明
|   `-- deployment.md          # 部署說明
|-- requirements.txt           # Python 相依套件的主要來源
|-- runtime.txt                # Python 版本
`-- netlify.toml               # Netlify build 設定
```

## 技術棧 Tech Stack

- Frontend: HTML, CSS, vanilla JavaScript
- Backend: Python
- Metadata extraction: `yt-dlp`
- Hosting target: Netlify static hosting + Netlify Functions

## 本地開發 Local Development

### 前置需求 Prerequisites

- Python 3.9
- `pip`
- 建議安裝 Netlify CLI 以便本地測試 serverless function

### 安裝相依套件 Install dependencies

```bash
pip install -r requirements.txt
```

如果你打算在本地測試 Netlify Function，也要確認 function 執行環境能讀到 `functions/requirements.txt`，而它目前會回頭引用根目錄 `requirements.txt`。

### 本地啟動 Run locally

目前 repo 雖然已補上最基本的 `netlify.toml`，但還沒有完整的本地開發腳本，所以要本地跑起來可能仍需要補一些設定。

一般 Netlify 專案常見的本地啟動方式如下：

```bash
netlify dev
```

不過在這個 repo 中，通常還要先確認：

- publish directory 是否為 `public`
- functions directory 是否為 `functions`
- Python function runtime 是否符合部署平台需求

更多可參考 [docs/deployment.md](D:/project/Codex/改作業專案/repo_read/docs/deployment.md)。

## API 規格 API Contract

### Endpoint

`POST /.netlify/functions/api`

### Request body

```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

### 成功回應範例 Example success response

```json
{
  "title": "Video title",
  "thumbnail": "https://...",
  "webpage_url": "https://www.youtube.com/watch?v=...",
  "download": {
    "url": "https://...",
    "format_id": "18",
    "ext": "mp4",
    "quality": "360p (mp4)",
    "filesize": 12345678,
    "protocol": "https"
  },
  "warning": "Direct media URLs can expire...",
  "duration": "12:34",
  "uploader": "Channel name"
}
```

### 可能錯誤回應 Possible error responses

- `405 Method Not Allowed`: 非 `POST` 請求
- `400 {"error":"Missing required field: url"}`: 缺少必要欄位
- `400 {"error":"Playlist URLs are not supported yet..."}`: 目前只支援單支影片
- `422 {"error":"No direct audio+video download format is available..."}`: 找不到合適的合併格式
- `500 {"error":"yt-dlp not installed"}`: 缺少相依套件
- `500 {"error":"..."}`: 擷取失敗、解析失敗或執行錯誤

## 限制與風險 Known Limitations

- 目前後端只挑選已經同時包含音訊與視訊的 progressive format，所以不是每支影片都能成功提供下載連結。
- 即使拿到 direct media URL，這類網址仍可能過期，或受到來源站 headers / IP 條件限制。
- 除了瀏覽器原生 `type="url"` 之外，目前幾乎沒有額外輸入驗證。
- 沒有 rate limiting、abuse protection、結構化觀測或審計機制。
- 目前沒有測試覆蓋。
- 雖然已補上最基本的 `netlify.toml`，但仍未涵蓋更完整的平台設定。

## 法律與使用聲明 Legal and Usage Note

請僅在符合 YouTube 服務條款、著作權法與所在地法規的前提下使用本專案。

Use this project only in ways that comply with YouTube's terms, copyright law, and applicable local regulations.

如果未來要公開部署，建議補上一份更清楚的 usage policy。

## 建議下一步 Suggested Next Steps

- 明確決定產品定位是 metadata analyzer 還是 full downloader
- 改善後端驗證與回傳格式
- 把部署流程寫成可以直接照做的文件
- 補上 function 與前端流程的測試
