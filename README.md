# Unplugged Grant Scout

A Claude agent that finds grant opportunities for Unplugged Wellness, screens them against the Unplugged brief and reports which ones are worth applying for.

## How it works

1. On the 1st of each month, a scheduled task on claude.ai starts a fresh Claude session.
2. Claude reads the **Unplugged Grant Brief (Scout Copy)** in Google Drive.
3. It searches city, county, Utah and national funders.
4. It rates each grant (Go, Go with caveats, Watch or No-go) and updates the **Unplugged Grant Tracker** sheet.
5. It writes a short report Doc, "Unplugged Grant Scout Report: <Month YYYY>," next to the tracker.

You can also run it any time by saying "run the grant scout" in a Claude chat.

## What's in this repo

| Path | What it is |
|---|---|
| `skill/unplugged-grant-scout/SKILL.md` | The scout's instructions. Edit this to change how it searches or rates grants. |
| `scheduled-task/monthly-prompt.md` | Settings and prompt for the monthly run. |
| `tracker/` | Snapshots of the tracker. The live version is the Google Sheet. |

## Editing

Ask Claude in a cloud session on this repo to make the change, for example "add Utah credit unions to the search list." Claude edits the file and saves it here. After a skill change, re-upload the zipped skill folder on claude.ai under Customize > Skills.
