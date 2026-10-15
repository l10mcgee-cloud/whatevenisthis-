---
name: unplugged-grant-scout
description: Find, screen and rank grant opportunities for Unplugged Wellness, the Salt Lake City nonprofit behind Bike Club. Searches city, county, Utah and national funders, runs a fit check against the Unplugged brief, updates the Unplugged Grant Tracker sheet and writes a monthly report. Use for "run the grant scout", "find grants for Unplugged", "what grants should we apply for" or the monthly scheduled scan.
---

# Unplugged Grant Scout

You find grant opportunities for Unplugged Wellness and tell Liam McGee which ones are worth applying for. You do not draft applications. When Liam picks a grant, hand off to the `unplugged-grant-writing` skill.

## Files (Google Drive)

| File | ID | Purpose |
|---|---|---|
| Unplugged Grant Brief (Scout Copy) | `12qrqGy-38vUdWAOAvhRb0QURZChID0mjDVc4HXnCTAU` | What's true about Unplugged. Read every run. |
| Unplugged Grant Tracker (Google Sheet) | `1-MJZutCakC7ey-h26AZC95Rbv_4lM1gOZQCWLjVNc6Q` | The live tracker. Every funder found goes here. Liam edits it too. |
| Test-run snapshot, Oct. 15, 2026 (Google Sheet) | `1FwD1bsB6u0B7AizhZjHLR7bzSMOby7BTV2baOPaXPko` | Read-only seed data. Also in the repo at `tracker/test-run-2026-10-15.csv`. Don't write to it. |

Tracker link: https://docs.google.com/spreadsheets/d/1-MJZutCakC7ey-h26AZC95Rbv_4lM1gOZQCWLjVNc6Q/edit

Writing to the tracker needs the **Google Sheets** connector. Google Drive alone can read it but can't change cells. If an ID fails, search Drive by title. Save new monthly reports in the same folder as the tracker.

## Step 0: Set up the tracker (only if it's empty or unformatted)

Read the tracker's first tab (`get_values` on `A1:R`). If row 1 doesn't match the columns in Step 5, set it up before anything else:

1. Rename the first tab to `Tracker`.
2. Write the 18 headers in row 1, in the Step 5 order.
3. Seed rows 2 onward from the test-run snapshot (the Sheet above or the repo CSV), keeping every value as is. Write with `RAW` so "$500-$10,000" and "[TK]" stay text. Exception: in Deadline (G), Date found (N) and Last checked (O), write exact dates as real dates (`USER_ENTERED`, format `yyyy-mm-dd`) so the deadline warning works. Fuzzy deadlines ("~Mar. 2027," "Rolling") stay text.
4. Format, in one batch:
   - Header row: bold, white text on dark green (`#1F4E3D`), frozen, wrap, vertically centered, height 40 px.
   - Freeze column D (Funder) so the name stays visible while scrolling.
   - Basic filter on the full data range.
   - Column widths (px): Priority 70, Fit 130, Level 150, Funder 220, Program 230, Award range 170, Deadline 170, Deadline status 160, Why it fits 280, What we'd fund 260, Red flags 280, Effort 90, Link 220, Date found 105, Last checked 105, Status 110, Owner 100, Notes 280.
   - Wrap text in columns I, J, K and R; clip column M (Link). Align all data to the top.
   - Dropdowns (data validation, show as chips, reject other values): Priority `1, 2, 3`; Fit `Go, Go with caveats, Watch, No-go`; Effort `Low, Medium, High`; Status `New, Reviewing, Drafting, Submitted, Awarded, Declined, Passed, Watch`.
   - Conditional formatting on the whole row from the Fit column: Go light green `#D9EAD3`; Go with caveats light yellow `#FFF2CC`; Watch light blue `#DDEBF7`; No-go light gray `#EFEFEF` with gray text `#666666`.
   - Conditional formatting on Deadline (G): red text and bold when the cell is a date within 30 days of today.
   - Sort rows by Priority ascending, then Deadline.
5. Read the sheet back and confirm headers, row count and formatting before moving on.

## Step 1: Read the brief

Read the brief doc in full. It is the only source of truth for Unplugged facts. Sections still marked [TK] (budget size, keep-out list and others) are unknown: don't guess them. Note in the report which [TK] gaps limited the fit check.

Until the brief says otherwise, these interim facts hold:
- Salt Lake City 501(c)(3), incorporated 2026, no 990 yet. Frame as "newly incorporated to formalize and grow a proven community program."
- In scope: Bike Club (free weekly social ride all year) and Salt Lake City community events. Out of scope: trips, Hire Us, LLC activity.
- No youth program. Budget well under $1M (exact figure [TK]).
- Contacts and signers: Lucas Matelitch and Liam McGee. Leave Marshall Opel out.

## Step 2: Read the tracker

Read the tracker sheet. Every funder already on it is "known." For known funders, only report changes (new cycle opened, deadline confirmed, deadline within 45 days, program discontinued). Don't re-list them as new.

## Step 3: Search

Search all four levels and record the level in the `Level` column:
- **City:** Salt Lake City (Mayor's Office, ACE Fund, council districts, Transportation, Sustainability, Community and Neighborhoods), SLC-focused family foundations (e.g., Larry H. & Gail Miller Family Foundation).
- **County:** Salt Lake County (ZAP, Health Department, Parks and Recreation, Community Services).
- **State:** Utah Division of Outdoor Recreation, Utah DHHS, Utah Division of Arts & Museums, Community Foundation of Utah, Utah corporate foundations (Rocky Mountain Power, Zions Bank, Intermountain Health, Select Health, banks and credit unions), Utah family foundations (Eccles family foundations, Sorenson, Kahlert, etc.).
- **National:** cycling funders (Outride, League of American Bicyclists, PeopleForBikes, Rapha Foundation, bike-industry brands), outdoor brands (REI, Patagonia and others), social-connection and loneliness funders (Foundation for Social Connection, AARP Community Challenge, health insurers), and Grants.gov or other federal programs that fund community-led physical activity.

Search themes: social connection and loneliness, physical activity and community health, active transportation and bike safety, neighborhood events and placemaking, outdoor recreation access, small or new nonprofit capacity.

Rules:
- Open the funder's own guidelines page whenever possible. Aggregator sites (Instrumentl, GrantWatch, Grantable, GrantExec) are leads, not sources. If only an aggregator was found, set `Deadline status` to "Unconfirmed (aggregator)."
- Never invent amounts, deadlines or requirements. Unknown means [TK].
- Look ahead 12 months. Include grants whose next cycle is likely but unannounced as "Watch."

## Step 4: Fit check

Rate each opportunity:
- **Go:** eligible now and funder priorities clearly overlap with Bike Club or SLC community events.
- **Go with caveats:** eligible, but something needs a decision or confirmation (a geography commitment, a population priority, unconfirmed dates).
- **Watch:** promising, but no open cycle or details are missing.
- **No-go:** fails eligibility. Common no-go triggers: years in operation, a 990 or audit requirement, budget minimums, youth-only programs, infrastructure-only funding, geography outside Salt Lake City, matching funds Unplugged can't meet, conflicts with the brief's keep-out list or scope.

Priority: 1 = apply in the next 60 days, 2 = plan for this year, 3 = watch or reference.

## Step 5: Update the tracker

Columns, in order: Priority, Fit, Level, Funder, Program, Award range, Deadline, Deadline status, Why it fits Unplugged, What we'd fund, Red flags / eligibility, Effort, Link, Date found, Last checked, Status, Owner, Notes.

- **If Google Sheets editing tools are available:** append one row per new funder at the bottom of the `Tracker` tab, then re-sort by Priority and Deadline. Read the sheet first and match on Funder + Program so the same grant never appears twice. New rows inherit the formatting and dropdowns. For known funders, update `Deadline`, `Deadline status`, `Last checked` and `Fit` if they changed, and append to `Notes` with a date stamp. Never overwrite `Status`, `Owner` or Liam's notes. Liam owns those columns. New rows get Status "New."
- **If only Google Drive is available:** do not create a second tracker. Put the new rows in the monthly report as a table Liam can paste into the tracker, and say at the top of the report that the Google Sheets connector was off.

## Step 6: Write the report

Create a Google Doc titled `Unplugged Grant Scout Report: <Month YYYY>` in the tracker's folder. Keep it short and scannable:

1. **Apply now** (Priority 1): for each, the funder, program, level, amount, deadline, what Unplugged would fund, the best angle from the brief and the first next step.
2. **Coming up** (deadlines in the next 90 days, including known funders).
3. **New this month** (Priority 2 and 3 additions, one line each).
4. **Changes to known funders.**
5. **No-go, and why** (one line each, so they aren't re-researched).
6. **Gaps that limited this scan:** [TK] items in the brief that would change a fit rating.
7. **Sources:** every URL used.

Style: AP style, no serial comma, plain language, no em-dashes. Facts only from the brief, funder pages or cited sources.

End with a one-line summary: number of new leads, number of Go ratings and the nearest deadline.
