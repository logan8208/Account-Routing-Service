I set up this project "C:\Users\<user>\Documents\Programming-and-projects\Csessions\Csessions - account exercise - 10-12-2026" and your job is to do the following - 

Before taking any action, make sure you read all instructions/associated files fully and let me know if there is any clarification you need from me on anything at all, and then send me the plan you make to complete all instrutions, in order of the actions you plan to take and things you will have me test along the way.

Make sure you always follow the additional rules in "C:\Users\<user>\Documents\Programming-and-projects\Csessions\Csessions - account exercise - 10-12-2026\rules.md" file every step of the way.

By the way, keep a log file from the very beginning and in it log actions of steps/actions you take and changes you make and corrections you make and self-corrections you make as you go.  I also need you to log prompts I give you/changes I make/updated decisions I make for this project and updated instructions I give you. Also include in the log which AI tools are used for this project (Claude Code terminal, model type, any other AI tools I give you permission to use, etc.), things I have delegated to you and things I tell you that I will work on myself for this project, things that you may produce wrong on accident and how I caught that it was wrong and asked you to correct it, where any of your judements (calls) around scoring/etc on accounts in the accounts-XLSX.xlsx file were wrong and what I did about it (eg, how I ask you to correct it), and what the whole project cost in tokens and dollars, and all prompts/plans/instructions I give you (short summary versions). Make sure to group these things in the log by cateogory as they are all different categories of logged items.

Before you start anything or ask me any questions, create a CLAUDE.md where you can enter/remember all your instructions I give you and process of how the output you build is structured/coded by you, so that any software engineer in this company can understand how you built it. 

## The situation

Our sales team has six account executives. Marketing and partners keep adding accounts to the CRM faster than anyone can sort them. The data is messy in the ways CRM data is always messy. Nobody is sure which accounts are already customers, which ones are duplicates, and which rep should own what. And nobody has read the notes field on 2,000 accounts.

Your job is to build the thing that sorts it out and keeps it sorted.

## What you get

All companies, people, domains and notes in this exercise are fictional (I am running this project as a test exercise for which all outputs will be valuable). Any resemblancance to a real business is coincidence. Work only from the files "C:\Users\<user>\Documents\Programming-and-projects\Csessions\Csessions - account exercise - 10-12-2026\accounts-XLSX.xlsx" and "C:\Users\<user>\Documents\Programming-and-projects\Csessions\Csessions - account exercise - 10-12-2026\reps-XLSX.xlsx". Do not look companies up on the web or enrich them from outside sources, since anything you find will not match the data and will not be scored (as these are fictional accounts).

- `accounts-XLSX.xlsx`: about 2,000 accounts as exported from the CRM. Nothing has been cleaned.
- `reps-XLSX.xlsx`: the six reps, the region and segment each covers, and how many accounts they already own.
- `rules.md`: the routing rules as the sales manager wrote them, with a state-to-region list at the end. Treat this as the spec. Where the spec is silent or unclear, make a call and write it down and ask me for clarification/instrutions on interpretation. 

### Columns in accounts-XLSX.xlsx

| Column | Meaning |
|---|---|
| `account_id` | CRM record ID. Unique per row, not per company. |
| `company_name` | As entered. Reps and imports both create these. |
| `website` | As entered. Not normalized. |
| `country`, `city`, `state` | Headquarters, as entered. Any can be blank. `state` holds a Canadian province where relevant. |
| `employee_count` | From an enrichment vendor. Blank when the vendor had nothing. |
| `funding_stage` | Last known round, or Bootstrapped, Public, Private Equity, Unknown. |
| `last_funding_year` | Year of the last round or IPO. Blank when unknown. |
| `industry` | From the enrichment vendor. |
| `existing_spend_usd_t12m` | Dollars this record has spent with us in the trailing 12 months. Zero for most rows. |
| `notes` | Free text from reps, imports, and marketing. Sometimes useful, sometimes stale. |

## What you build

Before any action you take, make sure I have tested and approved what you did in the previous step. Unless/until I say this approval is no longer necessary.

1. **Ingest and clean.** Load the accounts, normalize domains, identify duplicates and related records, and flag anything you could not resolve. Nothing gets silently dropped. If a row is excluded, the output you give in the web UI says why. Some relationships between rows are only visible in the "notes" column. Give me your thoughts on whether you think a rule or your AI/LLM inference as Claude should find them, and say why. For traceability - before you make any changes in the accounts-XLSX.xlsx file, duplicate the columns that are in there now and do not make any edits to the original columns, so that I can see the before/after edits you make. 
2. **Classify the use case.** For every eligible account, read the notes and industry and assign one use case: `call_analytics`, `voice_agent`, `meeting_notes`, `media_captions`, `clinical_documentation`, `legal_transcription`, `other`, or `none`. Use a structured output schema - make sure I approve the shema format/rules/use case assignment methodology you propse before you take action on this. Then hand-check a sample and report the error rate you measured, the sample size, and what it cost to run. We have ground truth for this step and will compare.
3. **Score and route.** Rank eligible accounts against the fit signals in the rules doc ("C:\Users\<user>\Documents\Programming-and-projects\Csessions\Csessions - account exercise - 10-12-2026\rules.md"), assign them to reps per the rules, respect book capacity, and produce a reason for every assignment that a rep could read. The reason should be written by you, but it has to be grounded in the data for that account. A rep will notice if it is not.
4. **Expose it.** Create a small web UI that shows each rep's book with the reasons. This UI will be very useful to the sales team (sales reps/managers will be the users)
5. **Document it.** A README covering (make sure to ask me my input on these questions for the README): how to run it, the clarifications I made when you asked when the rules were unclear, what I myself would add as improvements to this project/the output with another day, and one paragraph written by you for the sales manager explaining what the output is and what they should double check.

## Deliverables

- A GitHub repo with the code, the README, and the log file.
- The output files: cleaned accounts file, exclusions with reasons, use-case classifications, and the rep assignments with reasons. Once I approve of the final accounts-XLSX.xlsx verions, you should then convert it to a CSV file once I ask you to, in order for the project to be complete.
- A web UI and instructions to anyone in the company on how they can run it locally on their own computer. Do not deploy it anywhere.

## Things to make sure to ask yourself as you complete this (ie make sure you do all these things):

1. Did you catch the data problems, and did you handle them the way a careful person would rather than the fastest way?
2. Did you verify what you've produced before having me test it, and can you show me how you've done so? A measured error rate beats "it looked right."
3. Where the rules were unclear, did you ask me about it and have me make a defensible call and then did you document it?
4. Can a rep or a sales manager understand every decision you/I made regarding the accounts?
5. Could someone else run and maintain this final output?

Before taking any action, make sure you read all instructions/associated files fully and let me know if there is any clarification you need from me on anything at all, and then send me the plan you make to complete all instrutions, in order of the actions you plan to take and things you will have me test along the way.