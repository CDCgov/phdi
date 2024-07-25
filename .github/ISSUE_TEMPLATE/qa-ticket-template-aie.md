---
name: AIE QA Ticket Template
about: Template for eCR Viewer QA efforts
title: ''
labels: aie, quality-assurance-testing
assignees: ''

---

## Action Requested
As part of our efforts to QA the eCR Viewer please thoroughly test the following eCR in the eCR viewer: [Link to eCR ##: ID]()

## Acceptance Criteria
- [ ] The eCR has been run through orchestration and the pipeline
- [ ] The eCR has been viewed in the Viewer and compared side by side to the original XML/HTML file
- [ ] The eCR is appearing properly in the non-integrated homepage table
- [ ] All discovered issues are captured and added to our QA spreadsheet [link here]

## Basic process for comparing eCR Viewer output and original eCR

Steps to follow:
1. Go through the eCR Viewer fields from top to bottom
2. For every field in the eCR Viewer, do the following:
      a. Check that you can find the data somewhere in the original HTML or XML
      b.  Check the content of the fields to see if they are the same or different
3. Then, looking at the original eCR HTML, do a quick scroll through to see if there is any data or sections present that we aren't showing in the eCR Viewer

Things to look out for:
- **Do we have only some of the data that you can see in the HTML or XML? Does it seem like it could be important information to users?** 
  - for ex: if the HTML says "Race: White, European" and ours says "Race: White" --> we will want to note that as a problem that we are missing some data that is available!
- **Does the formatting of the data look odd/different?** 
  - for ex: did we get rid of page breaks such that narrative text is an overwhelming wall of text?
- **Are all addresses and phone numbers available in the HTML or XML available somewhere in our viewer?** 
  - we want to make sure we aren't missing any potential contact info for facilities that an end user may need to call for follow up
- **Do you notice anything that seems like a bug with our Viewer?** 
  - for ex: is there a field showing up with no data in it? is there an edge case with the eCR data you're looking at that we didn't account for?
