# 架構說明 Architecture

## 概覽 Overview

這個專案是一個「靜態前端 + serverless 後端」的小型 Web 應用。

This project is a small web app built with a static frontend and a serverless backend.

主要組成如下：

- 前端位於 `public/`
- 後端位於 `functions/api.py`
- 後端透過 `yt-dlp` 擷取影片資訊
- 預期部署平台為 Netlify static hosting + Netlify Functions

## 請求流程 Request Flow

1. 使用者在表單中輸入 YouTube URL。
2. `public/app.js` 攔截表單送出事件。
3. 前端送出 `POST /.netlify/functions/api`。
4. Function 解析 JSON body，讀取其中的 `url`。
5. Function 在 handler 內動態載入 `yt_dlp`，以降低 cold start 成本。
6. Function 讀取完整資訊與格式列表，但不直接執行下載。
7. Function 從 `formats` 中挑選同時包含音訊與視訊、且協定為 `http` 或 `https` 的格式。
8. Function 回傳精簡 JSON 給前端，包含選中的 `download` 資訊。
9. 前端把結果渲染成卡片，顯示影片資訊、畫質與下載入口。

## 為什麼後端採用輕量擷取 Why Lightweight Extraction Is Used

從目前程式碼來看，這個實作仍然有意避免 serverless 環境中的過重流程，但已不再使用先前只取 flat metadata 的做法。

The current implementation appears optimized to reduce timeout risk and startup overhead in a serverless environment.

目前的設計重點是：

- `yt_dlp` 不是在模組載入時 import，而是在 handler 內 import
- 不做 server-side 合併下載，而是只挑選已經合併好的 progressive format
- 僅接受 `http` 或 `https` 的直接媒體格式，排除 manifest 型態

這樣做的好處是仍然維持較輕的 serverless 流程，同時比原本單純回傳原始網址更接近真正可下載；代價則是某些只提供分離音視訊流的影片會直接回錯誤，而不是偽裝成可下載。

## 重要行為取捨 Important Behavioral Tradeoff

目前的 UI 與後端語意已經比較對齊，因為後端只有在找到可直接使用的合併格式時才會提供下載連結。

In its current form, the UI and backend are better aligned: a download link is only returned when a direct audio+video format is available.

實際上現在的規則是：

- 若找得到 audio+video 合併格式，就回傳該格式的直接 URL
- 若只有分離音訊流與視訊流，則回傳明確錯誤
- 不再退回原始 YouTube 頁面作為假下載連結

所以若要更精準描述目前產品行為，比較接近：

「分析 YouTube 影片資訊，並在可用時提供一個直接下載的合併格式」

而不是：

「對所有 YouTube 影片都能穩定輸出最高畫質下載」

## 前端責任 Frontend Responsibilities

前端目前負責：

- 收集使用者輸入
- 呼叫 serverless function
- 顯示 loading 狀態
- 先讀文字再 parse JSON，以避免回應格式異常時直接爆掉
- 顯示成功卡片或錯誤卡片

其中一個不錯的地方是，前端對非 JSON 回應有做防守性處理，能把部分純文字錯誤也呈現出來。

## 後端責任 Backend Responsibilities

後端目前負責：

- 僅接受 `POST`
- 載入 `yt_dlp`
- 擷取基本影片資訊
- 將結果整理成 JSON 回傳
- 捕捉與記錄執行錯誤

後端目前還沒有處理：

- URL 驗證
- domain allowlisting
- 結構化錯誤分類
- retry 機制
- rate limiting
- audit logging
- 分離音訊與視訊流的 server-side 合併

## 檔案角色 File Notes

- `functions/api.py` 是真正有在執行的 Function
- `public/app.js` 包含前端請求與畫面渲染流程
- Python 相依套件以 repo 根目錄 `requirements.txt` 為主要來源，`functions/requirements.txt` 只負責轉接引用
- `netlify.toml` 已補上最基本的 build 設定

## 架構風險 Architecture Risks

- 部署設定目前只有最小骨架，仍有部分平台細節尚未明文化
- 下載連結可靠度仍依賴 `yt-dlp` 回傳格式與上游站限制
- 某些 URL 或上游狀況下仍可能發生 serverless timeout
- 缺少測試會讓後續重構風險提高
