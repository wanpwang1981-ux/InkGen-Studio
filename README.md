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

### 3. 如何使用：創建一個人格設定檔

一切準備就緒後，您可以使用 `main.py` 中的命令列介面來創建您第一個作家的人格。

**使用範例：**

假設您想模仿作家「倪匡」，並且您已經準備好了兩個包含他作品的文字檔案 (`ni_kuang_sample1.txt`, `ni_kuang_sample2.txt`)。

執行以下命令：

```bash
python -m src.main create-persona \
    --author "倪匡" \
    --samples "path/to/your/ni_kuang_sample1.txt" "path/to/your/ni_kuang_sample2.txt" \
    --output "personas/ni_kuang.json"
```

**參數說明：**
*   `--author`: 您想模仿的作家名稱。
*   `--samples`: 一個或多個包含作家作品的文字檔案路徑。
*   `--output`: 生成的人格設定檔 (JSON 格式) 的儲存路徑。

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