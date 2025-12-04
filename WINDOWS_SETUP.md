# 🪟 Windows Setup Guide

Complete guide for setting up the Alta parking bot on Windows.

## Step 1: Install Python

1. **Download Python:**
   - Go to [python.org/downloads](https://www.python.org/downloads/)
   - Download the latest Python 3.x for Windows
   - **IMPORTANT:** During installation, check ✅ "Add Python to PATH"

2. **Verify Installation:**
   Open Command Prompt (search "cmd" in Start menu) and run:
   ```cmd
   python --version
   ```
   Should show Python 3.x.x

## Step 2: Get the Code

**Option A - Using Git:**
```cmd
cd %USERPROFILE%\Desktop
git clone [YOUR_REPO_URL] whatevenisthis-
cd whatevenisthis-
git checkout claude/alta-parking-bot-01M3SzWZfzNVcxp3xkbd6628
```

**Option B - Download Directly:**
1. Download the repository as a ZIP from GitHub
2. Extract to your Desktop
3. Open Command Prompt and navigate to the folder:
   ```cmd
   cd %USERPROFILE%\Desktop\whatevenisthis-
   ```

## Step 3: Install Dependencies

In Command Prompt (in the bot folder):
```cmd
pip install -r requirements.txt
playwright install chromium
```

This will:
- Install the required Python packages
- Download Chromium browser (~300MB)

## Step 4: Verify Credentials

Your credentials are already in the `.env` file. To check/edit:

```cmd
notepad .env
```

Make sure your password is correct. Save and close if you make changes.

## Step 5: Test the Bot

Run the bot in test mode (visible browser):

```cmd
python alta_parking_bot.py --test
```

This will:
- Open a browser window (you can watch it work!)
- Log into the Alta parking site
- Take screenshots for debugging
- Stay open for 30 seconds

**Check the screenshots created:**
- `after_login.png` - Login successful?
- `dashboard.png` - Reservation interface visible?

If it works, great! If not, send me the screenshots.

## Step 6: Set Up Automatic Scheduling

To run the bot automatically every Sunday at 3pm MST:

1. **Run the setup script as Administrator:**
   - Right-click on `setup_scheduler.bat`
   - Select "Run as administrator"
   - Follow the prompts

2. **Verify in Task Scheduler:**
   - Press Win+R, type `taskschd.msc`, press Enter
   - Look for "Alta Parking Bot" in the Task Scheduler Library
   - You can edit, disable, or delete it from here

### Timezone Adjustment (if not in MST)

If you're not in Mountain Standard Time:

1. Open Task Scheduler (`taskschd.msc`)
2. Find "Alta Parking Bot"
3. Double-click to edit
4. Go to "Triggers" tab
5. Edit the trigger and change the time:
   - **PST (Pacific):** Set to 2:00 PM
   - **CST (Central):** Set to 4:00 PM
   - **EST (Eastern):** Set to 5:00 PM
   - **Adjust as needed for your timezone to match 3pm MST**

## Common Commands

All commands should be run in Command Prompt from the bot folder:

```cmd
cd %USERPROFILE%\Desktop\whatevenisthis-
```

- **Test the bot:** `python alta_parking_bot.py --test`
- **Run the bot:** `python alta_parking_bot.py`
- **View logs:** `type alta_parking_bot.log`
- **Edit credentials:** `notepad .env`

## Troubleshooting

### "python is not recognized"
- Python isn't in your PATH
- Reinstall Python and check ✅ "Add Python to PATH"
- OR use the full path: `C:\Python3x\python.exe` instead of `python`

### "pip is not recognized"
- Same as above - Python not in PATH
- OR try: `python -m pip install -r requirements.txt`

### Task Scheduler doesn't run
- Make sure you created the task as Administrator
- Check that Python path is correct in the task
- Check the task history in Task Scheduler for errors

### Browser errors
- Run: `playwright install chromium`
- Make sure you have enough disk space (~300MB for browser)

## File Paths in Windows

Windows uses backslashes in paths:
- ✅ `C:\Users\YourName\Desktop\whatevenisthis-`
- ❌ `C:/Users/YourName/Desktop/whatevenisthis-` (this works too in Python, but Windows style is backslash)

## Next Steps

After your first successful test run, share the screenshots with me so I can complete the reservation clicking logic!

## Differences from macOS/Linux

- Uses `python` instead of `python3`
- Uses `pip` instead of `pip3`
- Uses Task Scheduler instead of cron
- Uses Command Prompt instead of Terminal
- Uses `notepad` instead of `nano` for editing files
- Uses `.bat` scripts instead of `.sh` scripts

Everything else works the same! 🎿
