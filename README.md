# Info Digest — Setup Guide

Daily AI intelligence briefing: reads your OS context, researches the web via Claude, and pushes a digest page to Notion.

## 1. Install dependencies
```
pip install anthropic notion-client python-dotenv
```

## 2. Create a .env file in the same folder as info_digest.py
```
ANTHROPIC_API_KEY=your_key_here
NOTION_API_KEY=your_key_here
```

Get your keys:
- Anthropic: https://console.anthropic.com → API Keys
- Notion: https://www.notion.so/my-integrations → New integration → copy "Internal Integration Secret"
  - Then open your "Info Digest" page in Notion → click "..." → Connections → connect your integration

## 3. Run manually
```
python info_digest.py
```

## 4. Automate with cron (Mac/Linux — runs at 7am every day)
Open terminal and run:
```
crontab -e
```
Add this line (update path to match where your script lives):
```
0 7 * * * /usr/bin/python3 /Users/yourname/info_digest.py >> /Users/yourname/digest.log 2>&1
```

## 5. Windows alternative (Task Scheduler)
- Open Task Scheduler
- Create Basic Task → Daily → 7:00 AM
- Action: Start a program → python.exe → argument: C:\path\to\info_digest.py

## Troubleshooting
- "Module not found": run pip install again, make sure you're using the right python environment
- "Unauthorized" from Notion: make sure you connected the integration to the Info Digest page (step 2)
- "Invalid API key": double-check your .env file has no spaces around the = sign
