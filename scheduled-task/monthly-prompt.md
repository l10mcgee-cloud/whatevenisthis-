# Monthly scheduled task: Unplugged Grant Scout

- **Name:** Unplugged Grant Scout
- **When:** 1st of each month, 7:55 a.m. Mountain (`CRON_TZ=America/Denver 55 7 1 * *`)
- **Mode:** fresh session each run, push and email notifications on
- **Needs:** Google Drive connector (and Google Sheets, so it can edit the tracker in place)

If you change the steps in `skill/unplugged-grant-scout/SKILL.md`, update the prompt below to match and paste it into the scheduled task on claude.ai.

## Prompt

Run the monthly Unplugged Grant Scout for Liam McGee (board member and co-writer, Unplugged Wellness). If the `unplugged-grant-scout` skill is available, invoke it and follow it. If not, follow the instructions in `skill/unplugged-grant-scout/SKILL.md` from the l10mcgee-cloud/whatevenisthis- repository; they are the source of truth.

Key files (Google Drive):
- Unplugged Grant Brief (Scout Copy), Doc ID 12qrqGy-38vUdWAOAvhRb0QURZChID0mjDVc4HXnCTAU
- Unplugged Grant Tracker, Sheet ID 1FwD1bsB6u0B7AizhZjHLR7bzSMOby7BTV2baOPaXPko

Steps: read the brief, read the tracker, search city, county, Utah and national funders, run the fit check, update the tracker (never overwrite Status, Owner or Liam's notes), then create "Unplugged Grant Scout Report: <Month YYYY>" in the tracker's folder. Finish with a one-line summary: new leads, number of Go ratings, nearest deadline and the report link.
