# 🚀 Quick Start Guide

Get the Alta parking bot running in 5 minutes!

> **Windows Users:** See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for Windows-specific instructions.
>
> **macOS/Linux Users:** Continue below.

## Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
playwright install chromium
```

## Step 2: Verify Your Credentials

Check that your login info is correct in the `.env` file:
```bash
cat .env
```

If the password needs updating:
```bash
nano .env
```
(Save with Ctrl+X, then Y, then Enter)

## Step 3: Test Run

Run the bot with a visible browser to make sure it works:

```bash
python3 alta_parking_bot.py --test
```

Watch it log in and take screenshots. This helps verify everything works!

## Step 4: Check Screenshots

After the test run, look at:
- `after_login.png` - Login successful?
- `dashboard.png` - Can you see the reservation interface?

If something looks wrong, let me know and we'll fix it!

## Step 5: Run Production Mode

Once the test works, run it normally (headless):

```bash
python3 alta_parking_bot.py
```

## Step 6: Set Up Automatic Scheduling

Run the setup script:

```bash
./setup_scheduler.sh
```

This will configure the bot to run automatically every Sunday at 3pm MST!

## That's it! 🎉

The bot is now installed and will automatically reserve your parking each week.

## Common Commands

- **Test the bot:** `python3 alta_parking_bot.py --test`
- **Run the bot:** `python3 alta_parking_bot.py`
- **View logs:** `tail -f alta_parking_bot.log`
- **Check schedule:** `crontab -l`

## Need Help?

Check the full [README.md](README.md) for detailed troubleshooting and customization options.
