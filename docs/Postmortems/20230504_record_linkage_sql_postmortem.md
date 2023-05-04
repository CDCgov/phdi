# 2023-05-04 Record Linkage SQL Injection Postmortem

**Postmortem Owner:** Marcelle, Dan

**Meeting Scheduled For:** Engineering Sync @ 10:30am PT on 5/4/23

## Overview
During an end-to-end run of the DIBBs pipeline with synthetic data, we discovered an error where a FHIR bundle [could not connect](https://skylight-hq.slack.com/archives/C03UF70CKGE/p1682360691930109?thread_ts=1682353411.011679&cid=C03UF70CKGE) to the MPI database for record linkage because the MRN contained an apostrophe, which early-terminated the SQL code used to retrieve blocking data from the MPI database. 

## Contributing Factors
- The queries to the MPI did not include any measures to prevent SQL injection attacks, even unintentional ones such as "Patient's Medical Record Number".
- When switching code contexts, i.e., from Python to SQL, we did not consider ramifications of using a different language and framework, such as externally connecting to PHI. 
- The test data we used initially did not include any single quotes and the test data that uncovered this issue included a single quote by accident; we were lucky this was discovered at all!

## Resolution
We added functionality to sanitize the SQL queries ([#512](https://app.zenhub.com/workspaces/dibbs-63f7aa3e1ecdbb0011edb299/issues/gh/cdcgov/phdi/512)), moving from raw SQL statements like "SELECT * FROM table;" to using [SQL composition](https://realpython.com/prevent-python-sql-injection/#passing-safe-query-parameters) to pass in parameters for the queries as [Literals](https://www.psycopg.org/docs/sql.html#psycopg2.sql.Literal). This took a little extra time because of the specifics of our queries, i.e., jsonb queries necessitate a lot of single quotes. 

Future resolutions/bigger picture items to consider:
- How can we handle switching languages/contexts both in development and code review?
- How can we develop more robust test data to potentially uncover issues like this earlier?

## Impact
5+ hours debugging and implementing solution

## Timeline
**Time (ET)**|**Event**
:-----:|:-----:
03-29-2023|MPI query code implemented
04-23-2023|Problem discovered with end-to-end pipeline testing
04-24-2023|Resolution implemented


## How’d We Do?
All the following sections should be filled out together as a team during the postmortem meeting.

### What Went Well?
- List anything the team did well and want to call out.
- Lots of pairing and collaboration
- Fairly quick turnaround time (2 days) considering the change to the approach

### Where Did We Get Lucky?
- The test file happened to have an apostrophe; not all patient medical record numbers included them
-

### What Didn’t Go So Well?
- List anything that could have gone better. The intent is that we should follow up on all points here to improve our processes.
- Error messages were not robust; the issue wasn't that we couldn't connect to the DB

### What Did We Learn?
- List any findings that came out of the incident.
- Using as close to real data when testing
- More integration tests

## Potential Action Items
Explore potential action items grouped by the themes discussed in What Didn’t Go So Well. 
- Re-organize assets by what the data _is_, e.g., FHIR bundles that can be re-used for testing across BBs
- Update RL error messages
- Update call to RL endpoint such that there are 3 separate try/except blocks instead of 1 try/except with 3 SDK functions within the same block; more intentional about designing try/except blocks
- Spike: Investigate other DB connection packages, e.g., SQLAlchemy vs. pyscopg
- Adjusting error response to not include the entire bundle (when failing?) so that it is easier to see the error message OR return message before the FHIR bundle so it is easier to see the message contents

Examples: 
1. any fixes required to prevent the contributing factor in the future
2. any preparedness tasks that could help mitigate the problem if it came up again
3. any improvements to our incident response process (pages, alert thresholds, etc).

## Action Items
The action items we are committing to from the potential action Items. Each action item should be in the form of a Zenhub ticket.
- Error handling in RL endpoint
- Re-organizing response to include message earlier on
- Wash your hands and your sql strings (sanitize)

## Messaging

### Internal
This is a follow-up for employees. It should be sent out right after the postmortem meeting is over. It only needs a short paragraph summarizing the incident and a link to this wiki page.

### External
What are we telling customers, including an apology? (The apology should be genuine, not rote.)
