# 墨影生成所 (InkGen Studio) - 系統架構

## 1. 總覽

本文件定義了「墨影生成所」的技術架構。此架構旨在建立一個模組化、可擴展且高效的 AI 輔助寫作平台，能夠支援多個 AI 代理協同工作，最終實現網路小說的自動化創作。

## 2. 設計原則

*   **模組化 (Modularity):** 每個組件都有明確定義的職責，可以獨立開發、測試和升級。
*   **可擴展性 (Scalability):** 系統應能夠處理多部小說的同時創作，並支援未來新增更多 AI 代理或功能。
*   **可配置性 (Configurability):** 核心參數，如語言模型（LLM）的選擇、API 金鑰、人格設定檔等，都應易於配置。
*   **可追蹤性 (Traceability):** 所有創作過程（從草稿到最終版）都應被記錄和版本控制，便於追蹤和除錯。

## 3. 核心組件圖

```mermaid
graph TD
    subgraph "用戶介面 (User Interface)"
        CLI[命令列介面]
    end

    subgraph "核心系統 (Core System)"
        Orchestrator[流程協調器]
        TaskQueue[任務佇列 DB (SQLite/PostgreSQL)]
        VersionControl[版本控制器 (Git)]
    end

    subgraph "AI 代理 (AI Agents)"
        PersonaArchitect[AI 角色創建大師]
        LeadArchitect[首席架構師]
        Writer[碼字工]
        Refiner[修飾專家]
        Reader[專業讀者]
    end

    subgraph "外部服務 & 資料儲存 (External Services & Data Stores)"
        LLM[語言模型服務 (Gemini API)]
        VectorDB[向量資料庫 (ChromaDB)]
        FileSystem[檔案系統 (novels/, personas/)]
    end

    CLI --> Orchestrator
    Orchestrator --> TaskQueue
    Orchestrator --> LeadArchitect
    Orchestrator --> PersonaArchitect

    LeadArchitect --> Writer
    Writer --> Refiner
    Refiner --> Reader
    Reader -- "合格" --> Orchestrator
    Reader -- "不合格" --> Writer

    PersonaArchitect -- "生成人格設定檔" --> FileSystem
    LeadArchitect -- "讀取人格" --> FileSystem
    Writer -- "讀取人格" --> FileSystem

    LeadArchitect -- "查詢知識" --> VectorDB
    Writer -- "查詢知識" --> VectorDB
    Orchestrator -- "儲存知識" --> VectorDB

    LeadArchitect -- "呼叫 LLM" --> LLM
    Writer -- "呼叫 LLM" --> LLM
    Refiner -- "呼叫 LLM" --> LLM
    Reader -- "呼叫 LLM" --> LLM
    PersonaArchitect -- "呼叫 LLM" --> LLM

    Orchestrator -- "管理版本" --> VersionControl
    VersionControl -- "儲存小說" --> FileSystem
```

## 4. 組件詳細說明

### 4.1. 用戶介面 (User Interface)

*   **命令列介面 (CLI):** 在專案初期，我們將透過一個簡單的命令列介面來啟動專案、與「AI 角色創建大師」互動，以及監督創作過程。

### 4.2. 核心系統 (Core System)

*   **流程協調器 (Orchestrator):**
    *   **職責:** 整個系統的大腦。負責解析使用者指令、創建和分派任務給對應的 AI 代理、管理任務佇列，以及在章節完成後觸發版本控制和知識庫更新。
    *   **技術:** Python 應用程式，使用 `LangChain` 或 `AutoGen` 框架來管理 AI 代理之間的互動。

*   **任務佇列資料庫 (Task Queue DB):**
    *   **職責:** 儲存待處理的寫作任務、任務狀態、小說元數據等。確保即使系統中斷，任務也不會遺失。
    *   **技術:** 初期使用輕量級的 `SQLite`，未來可擴展至 `PostgreSQL`。

*   **版本控制器 (Version Control):**
    *   **職責:** 對 `novels/` 目錄下的每部小說進行版本管理。每個章節的每次修改（初稿、潤飾稿、最終稿）都會被提交 (commit)，形成完整的歷史記錄。
    *   **技術:** 直接整合 `Git` 命令列工具。

### 4.3. AI 代理 (AI Agents)

所有 AI 代理都將被設計為可配置的模組，它們從協調器接收任務，並透過 LLM 服務來完成其特定功能。

*   **AI 角色創建大師 (Persona Architect):** 負責與使用者互動，根據提供的材料生成並儲存特定作家風格的「人格設定檔」。
*   **首席架構師 (Lead Architect):** 負責小說的宏觀規劃，包括主題、大綱和章節劃分。
*   **碼字工 (Writer):** 根據章節大綱和上下文，生成初稿。
*   **修飾專家 (Refiner):** 對初稿進行語言潤飾和風格修正。
*   **專業讀者 (Reader):** 審核潤飾後的稿件，判斷其品質是否達標，並提供修改建議。

### 4.4. 外部服務 & 資料儲存 (External Services & Data Stores)

*   **語言模型服務 (LLM Service):**
    *   **職責:** 提供底層的自然語言生成能力。它將是一個可抽換的模組，允許我們在不同的模型（如 Gemini 系列）之間切換。
    *   **技術:** 一個 API 客戶端，內建 **多 API Key 輪換機制**，以提高請求成功率和管理成本。

*   **向量資料庫 (Vector Database):**
    *   **職責:** 儲存小說的共用知識庫，包括世界觀、角色設定、重要情節摘要等。AI 代理可透過語意搜尋來查詢，確保長文寫作的一致性。
    *   **技術:** 使用本地端的 `ChromaDB`，便於快速啟動和開發。

*   **檔案系統 (File System):**
    *   **職責:** 儲存實體的檔案。
    *   `novels/`: 每部小說一個子目錄，每個章節一個 `.txt` 或 `.md` 檔。
    *   `personas/`: 每個人格設定檔一個 `.json` 或 `.md` 檔。