# Monthly scheduled task: Unplugged Grant Scout

- **Name:** Unplugged Grant Scout
- **When:** 1st of each month, 7:55 a.m. Mountain (`CRON_TZ=America/Denver 55 7 1 * *`)
- **Mode:** fresh session each run, push and email notifications on
- **Connectors:** Google Drive and Google Sheets (both added Oct. 15, 2026)

If you change the steps in `skill/unplugged-grant-scout/SKILL.md`, update the prompt below to match and paste it into the scheduled task on claude.ai.

## Prompt

Run the monthly Unplugged Grant Scout for Liam McGee (board member and co-writer, Unplugged Wellness). Invoke the `unplugged-grant-scout` skill and follow its steps. If the skill isn't available, use `skill/unplugged-grant-scout/SKILL.md` from the GitHub repo l10mcgee-cloud/whatevenisthis- (branch unplugged-grant-scout).

Key files (Google Drive). These IDs override any file IDs in the skill:
- Unplugged Grant Brief (Scout Copy), Doc ID 12qrqGy-38vUdWAOAvhRb0QURZChID0mjDVc4HXnCTAU. Read every run.
- Unplugged Grant Tracker (live), Sheet ID 1-MJZutCakC7ey-h26AZC95Rbv_4lM1gOZQCWLjVNc6Q, tab "Tracker". This is the only sheet you write to. It is already set up and formatted; append new rows below the existing ones so they inherit formatting and dropdowns.
- Test-run snapshot, Sheet ID 1FwD1bsB6u0B7AizhZjHLR7bzSMOby7BTV2baOPaXPko. Old and read-only. Never write to it.

Order: read the brief, read the tracker, search city, county, Utah and national funders, run the fit check, update the tracker (never overwrite Status, Owner or Liam's notes; never duplicate a Funder + Program), then create "Unplugged Grant Scout Report: <Month YYYY>" as a Google Doc.

If Google Sheets tools are missing or the tracker can't be opened, don't create a second tracker. Put the new rows in the report as a paste-ready table and say why at the top.

Style: AP style, no serial comma, no em-dashes. Never invent amounts, deadlines or requirements; unknown means [TK]. Finish with a one-line summary: new leads, number of Go ratings, nearest deadline and the report link.
