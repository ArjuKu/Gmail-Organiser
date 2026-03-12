# Gmail Organiser

**AI-Powered Email Management with Google Sheets Control**

---

## About This Project

I'm not a coder by trade - my background covers Business and Political Science. Having recently learned the basics of Python, this is my first real project. A disclaimer: I'm not a computing expert, nor am I a product developer. This is simply a personal experiment rooted in solving a problem for myself and others who prefer a clean Gmail inbox without having to manually manage it, which is an arduous process.

### Built with Vibecoding

This project was built using **vibecoding** - a new way of building software where I describe what I want in plain language, and AI tools like [OpenCode](https://opencode.ai) write the actual code for me.

Think of it like pair programming, but instead of a human developer, I'm working with an AI assistant. I explain the problem, AI suggests solutions, we iterate together, and eventually something working emerges.

It's not about knowing all the syntax or being an expert - it's about understanding what you want to build and communicating that clearly. The AI handles the technical heavy lifting.

Built with Streamlit, Google Gmail API, and Google Sheets API.

---

## Features

- **AI Classification** - Automatically categorises emails by sender (Promotions, Social, Updates, Personal, etc.)
- **Incremental Scanning** - Only scans new emails after the first run
- **Google Sheets Control** - Make decisions in a spreadsheet, apply them to Gmail
- **Safety First** - Starred emails and Primary inbox are always protected
- **Lifetime Delete Counter** - Tracks how many emails you've trashed per sender

---

## Prerequisites

Before running, you'll need:

1. **Google Cloud Project** with Gmail API and Google Sheets API enabled
2. **OAuth credentials.json** (download from Google Cloud Console)
3. **HuggingFace Token** (optional - for AI classification, works without it)
4. **Google Sheet** (create one and share with your Gmail)

---

## Setup Guide

### Step 1: Clone or Download
```bash
git clone https://github.com/ArjuKu/Gmail-Organiser.git
cd Gmail-Organiser
```

### Step 2: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 3: Configure
1. Copy `config.template.yaml` to `config.yaml`
2. Fill in your details:
   - `user_email`: Your Gmail address
   - `token`: Your HuggingFace token (optional)
   - `spreadsheet_id`: Your Google Sheet ID (from the URL)

### Step 4: Get Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable Gmail API & Google Sheets API
3. Create OAuth credentials → Download as `credentials.json`
4. Place `credentials.json` in the project folder

### Step 5: Run
```bash
python -m streamlit run src/app.py
```

Or double-click `run_app.bat` (Windows)

---

## How It Works

1. **Scan** - Click "Scan Inbox" to analyse your emails
2. **Review** - Check the Google Sheet, make decisions (Keep, Label, Trash)
3. **Apply** - Click "Apply Decisions" to execute your choices

---

## Tech Stack

- **Python** - Core logic
- **Streamlit** - User interface
- **Google APIs** - Gmail & Sheets integration
- **Keyword Classification** - Works without AI (lightweight mode)

---

## Disclaimer

This tool modifies your Gmail account. Use with caution. Always review decisions in the Google Sheet before applying.

---

## License

MIT License - Feel free to use and modify!
