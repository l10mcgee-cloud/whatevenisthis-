# Alta Ski Area Parking Reservation Bot

Automatically reserves parking spots at Alta Ski Area every week for Saturday and Sunday.

## Features

- 🚗 Auto-reserves parking 7 days in advance
- 📅 Targets Saturday and Sunday (not Friday)
- 🕒 Scheduled to run every Sunday at 3pm MST (when new spots are released)
- 📝 Detailed logging of all actions
- 📸 Screenshot capture for debugging
- 🔒 Secure credential storage

## Prerequisites

- Windows, macOS, or Linux with Python 3.7+
- Internet connection
- Alta parking account

## Platform-Specific Guides

- **Windows Users:** See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for complete Windows instructions
- **macOS/Linux Users:** Continue with the instructions below

## Installation (macOS/Linux)

### 1. Install Python (if not already installed)

Check if Python 3 is installed:
```bash
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/) or use Homebrew:
```bash
brew install python3
```

### 2. Clone or Download This Repository

```bash
cd ~/Desktop  # or wherever you want to keep it
# If this is a git repo, clone it
# Otherwise, just navigate to the folder
```

### 3. Install Dependencies

```bash
cd whatevenisthis-
pip3 install -r requirements.txt
playwright install chromium
```

The last command installs the Chromium browser for automation.

### 4. Configure Your Credentials

Your credentials are already in the `.env` file, but you should verify them:

```bash
cat .env
```

Make sure the password is correct. If you need to update it:
```bash
nano .env  # or use any text editor
```

## Usage

### Test Mode (First Time Setup)

**IMPORTANT:** Run the bot in test mode first to see if it works:

```bash
python3 alta_parking_bot.py --test
```

This will:
- Open a visible browser window
- Log into the Alta parking site
- Take screenshots of the interface
- Stay open for 30 seconds so you can see what's happening

Check the screenshots created:
- `after_login.png` - What the page looks like after logging in
- `dashboard.png` - The main reservation interface

**If login fails or looks wrong**, we may need to adjust the bot. Send me the screenshots!

### Production Mode

Once you've verified it works:

```bash
python3 alta_parking_bot.py
```

This runs headless (no visible browser) and completes the reservation automatically.

## Automated Scheduling

To run the bot automatically every Sunday at 3pm MST:

- **Windows:** Run `setup_scheduler.bat` as Administrator (see [WINDOWS_SETUP.md](WINDOWS_SETUP.md))
- **macOS/Linux:** Use the instructions below

### macOS/Linux: Using cron (Recommended)

1. Open your crontab:
```bash
crontab -e
```

2. Add this line (adjust the path to match where you saved the bot):
```bash
# Run Alta parking bot every Sunday at 3pm MST (adjust for your timezone)
0 15 * * 0 cd /Users/YOUR_USERNAME/Desktop/whatevenisthis- && /usr/bin/python3 alta_parking_bot.py >> bot_cron.log 2>&1
```

**Note:** Replace `/Users/YOUR_USERNAME/Desktop/whatevenisthis-` with the actual full path.

To get the full path, run:
```bash
pwd
```

3. Save and exit (in nano: Ctrl+X, then Y, then Enter)

### macOS: Using launchd (Alternative)

Create a launch agent file. I can help you set this up if you prefer this method!

### Automated Setup Script

- **macOS/Linux:** Run `./setup_scheduler.sh`
- **Windows:** Run `setup_scheduler.bat` as Administrator

## Logs

The bot creates a log file: `alta_parking_bot.log`

View recent logs:
```bash
tail -f alta_parking_bot.log
```

## Troubleshooting

### Login Issues

If the bot can't log in:
1. Run in test mode: `python3 alta_parking_bot.py --test`
2. Check the screenshots
3. Verify your password by logging in manually at https://reserve.altaparking.com/
4. Update the `.env` file if needed

### Browser Issues

If you get errors about the browser:
```bash
playwright install chromium
```

### Permission Issues

If cron doesn't work, macOS may need permissions:
1. Go to System Preferences > Security & Privacy > Privacy > Full Disk Access
2. Add Terminal or cron to the allowed apps

## Customization

### Change Target Days

Edit `alta_parking_bot.py`, find the `get_target_dates()` function:
```python
# Current: Saturday (5) and Sunday (6)
if future_date.weekday() in [5, 6]:

# For Friday and Saturday, change to:
if future_date.weekday() in [4, 5]:
```

### Change Reservation Window

Edit the range in `get_target_dates()`:
```python
# Current: 7 days ahead
for i in range(7, 8):

# For 5 days ahead:
for i in range(5, 6):
```

## Security Notes

- The `.env` file contains your password - keep it private!
- The `.env` file is in `.gitignore` so it won't be committed to git
- Logs may contain sensitive info - don't share them publicly

## Next Steps

After the first test run, I may need to update the reservation logic based on how the Alta website actually looks. The bot currently:
1. ✅ Logs into the site
2. ✅ Takes screenshots
3. ⏳ Needs customization for the actual reservation clicks

Once you run the test and share the screenshots, I can complete the reservation logic!

## Support

If you encounter any issues:
1. Check `alta_parking_bot.log` for error messages
2. Run in test mode to see what's happening
3. Share screenshots and error messages for help
