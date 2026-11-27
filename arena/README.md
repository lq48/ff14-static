# 站位圖地板（給 xivplan 用）

xivplan（https://xivplan.netlify.app/）的場地設定可以填「Background image URL」。
這裡放 xivplan 沒有收錄的地板，依遊戲截圖描成線條圖，顏色使用 xivplan 的主題變數，深淺主題都會跟著換色。

| 檔案 | 副本／階段 | 網址 |
|---|---|---|
| fru-p2.svg | 絕伊甸 P2（希瓦·米特隆） | https://lq48.github.io/ff14-static/arena/fru-p2.svg |

- 絕伊甸 P1 用 xivplan 內建的 `/arena/e11.svg` 就好。
- 用法：xivplan 右側「Arena」→「Background image URL」貼上網址；場地形狀選圓形、600×600。
- 重新產生：`python arena/fru_p2.py`（比例依截圖量測，說明寫在程式開頭）。
- 只放自己描的線條圖，不放遊戲拆出來的圖檔或截圖。
