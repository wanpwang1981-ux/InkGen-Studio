# 墨影生成所 (InkGen Studio)

**標語：突破寫作瓶頸，專為網路小說設計的自動 AI 寫作機器人。**

---

## 總覽

墨影生成所是一個先進的 AI 輔助寫作專案，旨在利用一個由多個專業 AI 代理組成的協作團隊，自動化網路小說的創作流程。從故事構思、大綱建立、內文撰寫，到風格模仿與品質審核，我們的目標是建立一個能夠自主產出高品質、長篇連載內容的智慧系統。

## ✨ 目前功能

本專案目前處於早期開發階段，已完成第一個核心功能：

### **AI 角色創建大師 (AI Persona Architect)**

這是一個強大的「元代理」功能，能夠學習和模仿任何文學大師的寫作風格。您可以提供一位作家的數個文本範例，角色創建大師會自動分析其寫作風格、敘事節奏、常用詞彙和核心主題，並生成一個結構化的 **人格設定檔 (Persona Profile)**。

這個設定檔未來將能被其他寫作 AI 代理載入，以確保產出的內容帶有特定作家的獨特靈魂。

## 🚀 開始使用

### 1. 環境設定

首先，請確保您的系統已安裝 Python 3.8 或更高版本。

```bash
# 1. 複製本專案 (如果您是從外部取得)
# git clone <repository_url>
# cd inkgen-studio

# 2. 建立並啟用一個 Python 虛擬環境 (建議)
python -m venv venv
source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`

# 3. 安裝所有必要的套件
pip install -r requirements.txt
```

### 2. 配置 API 金鑰

本專案需要使用 Google Gemini API。請將您的 API 金鑰配置在環境變數中。

```bash
# 1. 複製範例設定檔
cp .env.example .env

# 2. 編輯新的 .env 檔案
# nano .env
```

在 `.env` 檔案中，將 `YOUR_API_KEY_HERE` 替換為您自己的一個或多個 Gemini API 金鑰。若提供多個金鑰，請用逗號分隔，系統會自動輪換使用。

**`.env` 檔案內容範例:**
```
GEMINI_API_KEYS=your_key_1,your_key_2
```

### 3. 如何執行 (How to Run)

本專案包含一個後端 API 服務和一個前端使用者介面。您需要同時啟動它們。

**A. 啟動後端 API 伺服器**

在您的終端機中，執行以下命令：

```bash
# 從專案根目錄執行
python -m uvicorn src.api_server:app --reload
```

您應該會看到類似 `Uvicorn running on http://127.0.0.1:8000` 的訊息。請保持這個終端機視窗開啟。

**B. 使用前端介面**

1.  打開您的網頁瀏覽器（如 Chrome, Firefox, Edge）。
2.  在瀏覽器中，直接打開專案中的 `frontend/index.html` 檔案。
    *   您可以使用檔案總管，將 `index.html` 檔案拖曳到瀏覽器視窗中。
    *   或者，在瀏覽器的地址欄中輸入 `file:///` 加上您專案的完整路徑，例如：`file:///path/to/your/inkgen-studio/frontend/index.html`

現在您就可以在網頁上看到「墨影生成所」的操作介面，並透過表單與後端 API 互動了。

### 4. (可選) 使用命令列介面

除了前端介面，您依然可以使用 `main.py` 中的命令列工具來執行所有核心功能。

**使用範例：**

```bash
# 初始化一個新專案
python -m src.main init --title "星際之夢" --outline "path/to/outline.json"

# 從專案開始生成小說
python -m src.main generate-novel --project "novels/星際之夢"
```

執行成功後，您會在 `personas/` 目錄下找到一個名為 `ni_kuang.json` 的檔案，裡面包含了對倪匡寫作風格的詳細分析。

## 📂 專案結構

```
.
├── docs/              # 存放系統架構、流程圖等設計文件
├── novels/            # 未來用於存放 AI 生成的小說專案
├── personas/          # 存放由「角色創建大師」生成的人格設定檔
├── src/               # 應用程式的主要原始碼
│   ├── agents/        # 包含所有 AI 代理的類別
│   ├── config.py      # 設定載入模組
│   ├── llm_service.py # Gemini API 服務層
│   └── main.py        # 命令列介面 (CLI) 入口
├── .env.example       # 環境變數設定範本
└── requirements.txt   # 專案依賴的 Python 套件
```

## 🗺️ 未來方向 (Roadmap)

接下來，我們將逐步實作 AI 團隊的其他核心成員：

*   **首席架構師 (Lead Architect):** 負責小說的宏觀規劃。
*   **碼字工 (Writer):** 負責根據大綱撰寫章節初稿。
*   **修飾專家 (Refiner):** 負責對初稿進行潤飾。
*   **專業讀者 (Reader):** 負責審核稿件品質。

敬請期待！