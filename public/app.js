document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const input = document.getElementById('videoUrl');
    const submitBtn = document.getElementById('submitBtn');
    const resultSection = document.getElementById('resultSection');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = input.value.trim();
        if (!url) return;

        // UI Loading State
        setLoading(true);
        resultSection.innerHTML = '';
        resultSection.classList.add('hidden');

        try {
            // Call Netlify Function (Standard path)
            const response = await fetch('/.netlify/functions/api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            // 先讀取文字內容，避免直接 parse JSON 失敗
            const textResponse = await response.text();

            if (!response.ok) {
                // 嘗試看看能不能解析錯誤訊息，不能就顯示原始文字
                try {
                    const errorJson = JSON.parse(textResponse);
                    throw new Error(errorJson.error || `伺服器錯誤: ${response.status}`);
                } catch (e) {
                    // 如果 textResponse 是 "Method Not Allowed" 或其他 HTML/Text
                    throw new Error(`請求失敗 (${response.status}): ${textResponse.slice(0, 100)}...`);
                }
            }

            // 成功狀況下解析 JSON
            let data;
            try {
                data = JSON.parse(textResponse);
            } catch (e) {
                throw new Error("伺服器回應格式錯誤 (Not JSON)");
            }

            renderResult(data);

        } catch (error) {
            console.error('Full Error:', error);
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    }

    function renderResult(data) {
        const { title, thumbnail, duration, uploader, url } = data;

        // Clean up the structure for clarity
        const card = document.createElement('div');
        card.className = 'glass-card result-card';

        card.innerHTML = `
            <div class="thumbnail-wrapper">
                <img src="${thumbnail}" alt="${title}" class="thumbnail">
            </div>
            <div class="video-info">
                <h2 class="video-title">${title}</h2>
                <div class="video-meta">
                    <span>👤 ${uploader}</span>
                    <span>⏱ ${duration}</span>
                </div>
                <a href="${url}" target="_blank" class="download-link" rel="noopener noreferrer" download="${title}.mp4">
                    <span>⬇ 下載影片</span>
                </a>
                <p style="margin-top: 10px; font-size: 0.8rem; color: #94a3b8;">如果點擊無法下載，請右鍵選擇「另存連結為...」或「另存影片」</p>
            </div>
        `;

        resultSection.appendChild(card);
        resultSection.classList.remove('hidden');
    }

    function showError(message) {
        const errorCard = document.createElement('div');
        errorCard.className = 'glass-card';
        errorCard.style.textAlign = 'center';
        errorCard.style.borderColor = '#ef4444';

        errorCard.innerHTML = `
            <p style="color: #ef4444; font-weight: 600;">❌ 錯誤</p>
            <p style="margin-top: 0.5rem;">${message}</p>
        `;

        resultSection.appendChild(errorCard);
        resultSection.classList.remove('hidden');
    }
});
