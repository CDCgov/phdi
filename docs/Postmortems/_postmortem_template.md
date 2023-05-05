# YYYY-MM-DD Title

**Postmortem Owner:** Your name goes here.

**Meeting Scheduled For:** Schedule the meeting on the "Incident Postmortem Meetings" shared calendar, for within 5 business days after the incident. Put the date/time here.

## Overview
Include a short sentence or two summarizing the contributing factors, timeline summary, and the impact. E.g. "On the morning of August 99th, we suffered a 1 minute SEV-1 due to a runaway process on our primary database machine. This slowness caused roughly 0.024% of alerts that had begun during this time to be delivered out of SLA."

## Contributing Factors
Include a description of any conditions that contributed to the issue. If there were any actions taken that exacerbated the issue, also include them here with the intention of learning from any mistakes made during the resolution process.

## Resolution
Include a description of what solved the problem. If there was a temporary fix in place, describe that along with the long-term solution.

## Impact
Be very specific here and include exact numbers.

## Timeline
Some important times to include: 
1. time the contributing factor began
1. time of the page
1. time that the status page was updated (i.e. when the incident became public)
1. time of any significant actions
1. time the SEV-2/1 ended
1. links to tools/logs that show how the timestamp was arrived at.

**Time (ET)**|**Event**
:-----:|:-----:
12-10-2021 12:31 PM|Description of an important event


## How’d We Do?
All the following sections should be filled out together as a team during the postmortem meeting.

### What Went Well?
- List anything the team did well and want to call out.

### Where Did We Get Lucky?
- List anything we got lucky on.

### What Didn’t Go So Well?
- List anything that could have gone better. The intent is that we should follow up on all points here to improve our processes.

### What Did We Learn?
- List any findings that came out of the incident.

## Potential Action Items
Explore potential action items grouped by the themes discussed in What Didn’t Go So Well. 

Examples: 
1. any fixes required to prevent the contributing factor in the future
2. any preparedness tasks that could help mitigate the problem if it came up again
3. any improvements to our incident response process (pages, alert thresholds, etc).

## Action Items
The action items we are committing to from the potential action Items. Each action item should be in the form of a Zenhub ticket.

## Messaging

### Internal
This is a follow-up for employees. It should be sent out right after the postmortem meeting is over. It only needs a short paragraph summarizing the incident and a link to this wiki page.

### External
What are we telling customers, including an apology? (The apology should be genuine, not rote.)
