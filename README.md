# Gmail Organiser

**AI-Powered Email Management with Google Sheets Control**

---

## About This Project

“The only thing worse than a funny bone is an ugly inbox.”

Fourteen years with Gmail taught me that Google’s filters are equivalent to using a butter knife when I need onions chopped. Same sender, new address? Still slips through. Unsubscribe link? A placebo. Labels? You're stuck making your own. I finally snapped and developed a script that does three things Gmail still won’t: it bulk-deletes every message from anyone who ever spammed me, spots the same sender even when they swap addresses, and pops up a yes/no on each label so I can dump the dead weight.

I call it Gmail Organiser. If your inbox feels like a storage unit you’re afraid to open, it can be yours too.

I'm not a coder by trade - my background covers Business and Political Science. Having recently learned the basics of Python, this is my first real project. A disclaimer: I'm not a computing expert, nor am I a product developer. This is simply a personal experiment to solve a problem for myself and others who prefer a clean Gmail inbox without having to manage it manually.

### My Introduction to Vibecoding

This is my first real dive into vibecoding, which allowed me to bridge what I envisioned with my lack of technical expertise. So if any experienced software/product developers are looking at this, I'd really appreciate your feedback!

Built with Streamlit, Google Gmail API, and Google Sheets API.

<img width="1535" height="851" alt="Image" src="https://github.com/user-attachments/assets/393ab2dd-c698-4297-a259-6af224260b51" />

---

## Project Structure

```
gmail-organiser/
├── app/                    # Main application code
│   ├── app.py             # Streamlit user interface
│   ├── auth.py            # Google OAuth authentication
│   ├── gmail_client.py    # Gmail API operations
│   └── sheets_client.py   # Google Sheets API operations
├── core/                  # Core business logic
│   ├── scan_senders.py    # Scans inbox, groups by sender
│   ├── apply_senders.py   # Applies decisions to Gmail
│   ├── classify_senders.py # Keyword classification
│   └── ai_classifier.py   # AI classification (optional)
├── config/                # Configuration files
│   └── config.template.yaml
├── docs/                  # Documentation
├── .gitignore
├── README.md
├── requirements.txt
└── run_app.bat           # Double-click to launch (Windows)
```

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
1. Copy `config/config.template.yaml` to `config/config.yaml`
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
python -m streamlit run app/app.py
```

Or double-click `run_app.bat` (Windows)

---

## How It Works

1. **Scan** - Click "Scan Inbox" to analyse your emails
2. **Review** - Check the Google Sheet, make decisions (Keep, Label, Trash)
3. **Apply** - Click "Apply Decisions" to execute your choices

<img width="1299" height="836" alt="Image" src="https://github.com/user-attachments/assets/b71c713d-ac72-4a27-90bc-1e8484e1f751" />

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
