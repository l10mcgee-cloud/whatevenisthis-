#!/bin/bash
# Setup script for scheduling the Alta parking bot on macOS

echo "🎿 Alta Parking Bot - Scheduler Setup"
echo "====================================="
echo ""

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Bot location: $SCRIPT_DIR"
echo ""

# Find Python3 path
PYTHON_PATH=$(which python3)
echo "Python3 path: $PYTHON_PATH"
echo ""

# Ask for timezone adjustment
echo "The bot should run every Sunday at 3pm MST."
echo "What timezone are you in? (For reference, MST is UTC-7)"
echo "Examples: PST (UTC-8), EST (UTC-5), MST (UTC-7)"
read -p "Enter your timezone offset from UTC (e.g., -8 for PST): " TZ_OFFSET

# Calculate the hour for cron based on timezone
# MST is 3pm = 15:00
# If user is in PST (-8) and MST is -7, they're 1 hour behind, so 2pm (14:00)
MST_OFFSET=-7
USER_OFFSET=$TZ_OFFSET
HOUR_DIFF=$((MST_OFFSET - USER_OFFSET))
LOCAL_HOUR=$((15 - HOUR_DIFF))

# Handle day wrapping
LOCAL_DAY=0  # Sunday
if [ $LOCAL_HOUR -lt 0 ]; then
    LOCAL_HOUR=$((LOCAL_HOUR + 24))
    LOCAL_DAY=6  # Saturday
elif [ $LOCAL_HOUR -ge 24 ]; then
    LOCAL_HOUR=$((LOCAL_HOUR - 24))
    LOCAL_DAY=1  # Monday
fi

echo ""
echo "To run at 3pm MST, the bot will run on your system at:"
echo "  Day: $([ $LOCAL_DAY -eq 0 ] && echo "Sunday" || ([ $LOCAL_DAY -eq 6 ] && echo "Saturday" || echo "Monday"))"
echo "  Time: ${LOCAL_HOUR}:00"
echo ""

# Create the cron entry
CRON_ENTRY="0 ${LOCAL_HOUR} * * ${LOCAL_DAY} cd ${SCRIPT_DIR} && ${PYTHON_PATH} ${SCRIPT_DIR}/alta_parking_bot.py >> ${SCRIPT_DIR}/bot_cron.log 2>&1"

echo "Cron entry to add:"
echo "$CRON_ENTRY"
echo ""

read -p "Would you like to add this to your crontab now? (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    # Backup existing crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null

    # Add new entry
    (crontab -l 2>/dev/null; echo "# Alta Parking Bot - runs every Sunday at 3pm MST"; echo "$CRON_ENTRY") | crontab -

    echo "✅ Cron job added successfully!"
    echo ""
    echo "To view your crontab: crontab -l"
    echo "To edit your crontab: crontab -e"
    echo "To remove the job later: crontab -e (then delete the line)"
else
    echo ""
    echo "Cron job not added. You can manually add it later with:"
    echo "  crontab -e"
    echo ""
    echo "Then add this line:"
    echo "$CRON_ENTRY"
fi

echo ""
echo "⚠️  IMPORTANT: macOS may require permissions for cron to work!"
echo "If the bot doesn't run automatically:"
echo "1. Go to System Preferences > Security & Privacy > Privacy"
echo "2. Select 'Full Disk Access' from the left sidebar"
echo "3. Click the lock to make changes"
echo "4. Click '+' and add '/usr/sbin/cron'"
echo ""
echo "Setup complete! 🎉"
