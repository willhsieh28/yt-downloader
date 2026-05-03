# 部署說明 Deployment Notes

## 目前狀態 Current Repository State

這個 repo 很明顯是朝 Netlify 部署設計的，但目前設定還不完整。

This repository appears intended for Netlify deployment, but part of the deployment setup is still implicit.

目前可以看到的訊號有：

- `functions/api.py` 的寫法符合 Netlify Function handler 風格
- `public/` 是靜態前端資產目錄
- `runtime.txt` 指定 Python `3.9`
- `netlify.toml` 已定義最基本的 `publish` 與 `functions` 目錄

雖然最基本的部署意圖已經寫進 repo，但更完整的平台細節仍未完全明文化。

## 預期部署模型 Expected Hosting Model

這個專案目前最合理的部署模型應該是：

- `public/` 作為靜態網站輸出目錄
- `functions/` 作為 Python serverless functions 目錄
- 前端透過 `/.netlify/functions/api` 呼叫後端

## Python 相依套件 Python Dependencies

專案目前仍有兩份 dependency 檔案：

- 根目錄 `requirements.txt`
- `functions/requirements.txt`

目前的設計是：

```text
requirements.txt              # 真正的相依套件來源
functions/requirements.txt    # 轉接引用 requirements.txt
```

這樣做的目的是保留 function 目錄下的需求檔入口，同時避免兩份內容長期漂移。

## 建議補上的 Netlify 設定 Recommended Netlify Configuration

這個 repo 很適合至少先補上類似下面的 `netlify.toml`：

```toml
[build]
  publish = "public"
  functions = "functions"
```

Depending on the target environment, additional settings may still be needed for Python function support.

也就是說，這份設定只是最基本骨架，未必代表最終完整可部署版本。

## 本地預覽 Local Preview

如果已安裝 Netlify CLI，常見的本地開發指令會是：

```bash
netlify dev
```

但在目前這個 repo 狀態下，啟動前通常還要再確認：

- publish directory 是否正確指向 `public`
- functions directory 是否正確指向 `functions`
- Python function 的執行方式是否符合本機與平台環境

## 常見失敗情境 Common Failure Modes

### 405 Method Not Allowed

原因 Cause:

- Function 只接受 `POST`

檢查方向 What to check:

- 呼叫方法是不是 `POST`
- 路徑是不是 `/.netlify/functions/api`

### 500 yt-dlp not installed

原因 Cause:

- Python runtime 無法 import `yt_dlp`

檢查方向 What to check:

- 相依套件是否已安裝
- serverless build 是否真的把 Python dependencies 帶進去
- 部署平台是否支援目前設定的 Python runtime

### 500 extraction failure

原因 Cause:

- URL 無效
- 上游擷取失敗
- timeout 或遠端封鎖

檢查方向 What to check:

- Function runtime logs
- 目標 URL 是否可正常存取
- 目前 `yt-dlp` 版本是否仍相容於該頁面行為

## 目前仍待補齊的部署缺口 Deployment Gaps To Resolve

- 視部署平台需求補上更完整的 `netlify.toml`
- 把實際部署流程寫成可直接照做的步驟
- 加上部署後 smoke test

## 建議驗收流程 Recommended Smoke Test

部署完成後，至少建議驗證以下流程：

1. 打開首頁。
2. 貼上一個有效的 YouTube URL。
3. 確認 Function 有回傳影片資訊。
4. 確認畫面能正確顯示標題、縮圖、時長與上傳者。
5. 確認下載連結行為符合目前產品定義。

最後一步特別重要，因為在目前後端設計下，那個連結不一定是真正的媒體直連。
