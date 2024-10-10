// @ts-check

import { test, expect } from "@playwright/test";

test.describe("querying with the TryTEFCA viewer", () => {
  test.beforeEach(async ({ page }) => {
    // Start every test on our main landing page
    await page.goto("http://localhost:3000/tefca-viewer");
  });

  test("landing page loads", async ({ page }) => {
    // Check that each expected text section is present
    await expect(
      page.getByRole("heading", { name: "Data collection made easier" }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "What is it?" }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "How does it work?" }),
    ).toBeVisible();

    // Check that interactable elements are present (header and Get Started)
    await expect(
      page.getByRole("link", { name: "TEFCA Viewer" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Go to the demo" }),
    ).toBeVisible();
  });

  test("unsuccessful user query: no patients", async ({ page }) => {
    await page.getByRole("button", { name: "Go to the demo" }).click();
    await page
      .getByLabel("Query", { exact: true })
      .selectOption("social-determinants");
    await page.getByRole("button", { name: "Advanced" }).click();
    await page
      .getByLabel("FHIR Server (QHIN)", { exact: true })
      .selectOption("HELIOS Meld: Direct");

    await page.getByLabel("First Name").fill("Ellie");
    await page.getByLabel("Last Name").fill("Williams");
    await page.getByLabel("Phone Number").fill("5555555555");
    await page.getByLabel("Medical Record Number").fill("TLOU1TLOU2");
    await page.getByRole("button", { name: "Search for patient" }).click();

    // Better luck next time, user!
    await expect(
      page.getByRole("heading", { name: "No Records Found" }),
    ).toBeVisible();
    await expect(
      page.getByText("No records were found for your search"),
    ).toBeVisible();
    await page
      .getByRole("link", { name: "Revise your patient search" })
      .click();
  });

  test("successful demo user query: the quest for watermelon mcgee", async ({
    page,
  }) => {
    await page.getByRole("button", { name: "Go to the demo" }).click();

    // Check that the info alert is visible and contains the correct text
    const alert = page.locator(".custom-alert");
    await expect(alert).toBeVisible();
    await expect(alert).toHaveText(
      "This site is for demo purposes only. Please do not enter PII on this website.",
    );
    await expect(
      page.getByRole("heading", { name: "Search for a Patient", exact: true }),
    ).toBeVisible();

    // Put in the search parameters for the elusive fruit person
    await page
      .getByLabel("Query", { exact: true })
      .selectOption("newborn-screening");
    await page
      .getByLabel("Patient", { exact: true })
      .selectOption("newborn-screening-referral");
    await page.getByRole("button", { name: "Fill fields" }).click();
    await page.getByLabel("First Name").fill("Watermelon");
    await page.getByLabel("Last Name").fill("McGee");
    await page.getByLabel("Date of Birth").fill("2024-07-12");
    await page.getByLabel("Medical Record Number").fill("18091");
    await page.getByLabel("Phone Number").fill("5555555555");
    await page.getByRole("button", { name: "Search for patient" }).click();

    // Make sure we have a results page with a single patient
    // Non-interactive 'div' elements in the table should be located by text
    await expect(
      page.getByRole("heading", { name: "Patient Record" }),
    ).toBeVisible();
    await expect(page.getByText("Patient Name")).toBeVisible();
    await expect(page.getByText("WATERMELON SPROUT MCGEE")).toBeVisible();
    await expect(page.getByText("Patient Identifiers")).toBeVisible();
    await expect(page.getByText("MRN: 18091")).toBeVisible();

    // Check that the info alert is visible and has updated to the correct text
    const alert2 = page.locator(".custom-alert");
    await expect(alert2).toBeVisible();
    await expect(alert2).toHaveText(
      "Interested in learning more about using the TEFCA Query Connector for your jurisdiction? Send us an email at dibbs@cdc.gov",
    );

    // Check to see if the accordion button is open
    await expect(
      page.getByRole("button", { name: "Observations", expanded: true }),
    ).toBeVisible();

    // We can also just directly ask the page to find us filtered table rows
    await expect(page.locator("tbody").locator("tr")).toHaveCount(5);

    // Now let's use the return to search to go back to a blank form
    await page.getByRole("button", { name: "New patient search" }).click();
    await expect(
      page.getByRole("heading", { name: "Search for a Patient", exact: true }),
    ).toBeVisible();
  });

  test("query using form-fillable demo patient by phone number", async ({
    page,
  }) => {
    await page.getByRole("button", { name: "Go to the demo" }).click();

    await page.getByLabel("Query", { exact: true }).selectOption("syphilis");
    await page
      .getByLabel("Patient", { exact: true })
      .selectOption("sti-syphilis-positive");
    await page.getByRole("button", { name: "Fill fields" }).click();

    // Delete last name and MRN to force phone number as one of the 3 fields
    await page.getByLabel("Last Name").clear();
    await page.getByLabel("Medical Record Number").clear();

    // Among verification, make sure phone number is right
    await page.getByRole("button", { name: "Search for patient" }).click();
    await expect(
      page.getByRole("heading", { name: "Patient Record" }),
    ).toBeVisible();
    await expect(page.getByText("Patient Name")).toBeVisible();
    await expect(page.getByText("Veronica Anne Blackstone")).toBeVisible();
    await expect(page.getByText("Contact")).toBeVisible();
    await expect(page.getByText("937-379-3497")).toBeVisible();
    await expect(page.getByText("Patient Identifiers")).toBeVisible();
    await expect(page.getByText("34972316")).toBeVisible();
  });

  test("social determinants query with generalized function", async ({
    page,
  }) => {
    await page.getByRole("button", { name: "Go to the demo" }).click();
    await page
      .getByLabel("Query", { exact: true })
      .selectOption("social-determinants");
    await page.getByRole("button", { name: "Fill fields" }).click();
    await page.getByRole("button", { name: "Search for patient" }).click();
    await expect(
      page.getByRole("heading", { name: "Patient Record" }),
    ).toBeVisible();
  });

  test("form-fillable STI query using generalized function", async ({
    page,
  }) => {
    await page.getByRole("button", { name: "Go to the demo" }).click();
    await page.getByLabel("Query", { exact: true }).selectOption("chlamydia");
    await page.getByRole("button", { name: "Fill fields" }).click();
    await page.getByLabel("Phone Number").fill("");
    await page.getByRole("button", { name: "Search for patient" }).click();
    await expect(
      page.getByRole("heading", { name: "Patient Record" }),
    ).toBeVisible();
  });
});

test.describe("Test the user journey of a 'tester'", () => {
  test.beforeEach(async ({ page }) => {
    // Start every test on direct tester page
    await page.goto("http://localhost:3000/tefca-viewer/query/test", {
      waitUntil: "load",
    });
  });

  test("query/test page loads", async ({ page }) => {
    // Check that interactable elements are present
    await expect(
      page.getByRole("button", { name: "Data Usage Policy" }),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: "TEFCA Viewer" }),
    ).toBeVisible();

    // Check that each expected text section is present
    await expect(
      page.getByRole("heading", { name: "Search for a Patient", exact: true }),
    ).toBeVisible();
    await expect(page.getByLabel("Query", { exact: true })).toBeVisible();
    await expect(page.getByLabel("Patient", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Advanced" })).toBeVisible();
  });

  test("Query for patient using auto-filled data", async ({ page }) => {
    await page
      .getByLabel("Query", { exact: true })
      .selectOption({ value: "newborn-screening" });
    await page
      .getByLabel("Patient", { exact: true })
      .selectOption({ value: "newborn-screening-referral" });
    await page.getByRole("button", { name: "Fill fields" }).click();
    await page.getByRole("button", { name: "Search for patient" }).click();

    // Make sure we have a results page with a single patient
    await expect(
      page.getByRole("heading", { name: "Patient Record" }),
    ).toBeVisible();
    await expect(page.getByText("Patient Name")).toBeVisible();
    await expect(page.getByText("WATERMELON SPROUT MCGEE")).toBeVisible();
    await expect(page.getByText("Patient Identifiers")).toBeVisible();
    await expect(page.getByText("MRN: 18091")).toBeVisible();
  });

  test("Query for patient by filling in data", async ({ page }) => {
    await page
      .getByLabel("Query", { exact: true })
      .selectOption("Newborn screening follow-up");
    await page.getByRole("button", { name: "Advanced" }).click();
    await page
      .getByLabel("FHIR Server (QHIN)", { exact: true })
      .selectOption("HELIOS Meld: Direct");
    await page.getByLabel("First Name").fill("Watermelon");
    await page.getByLabel("Last Name").fill("McGee");
    await page.getByLabel("Phone Number").fill("5555555555");
    await page.getByLabel("Date of Birth").fill("2024-07-12");
    await page.getByLabel("Medical Record Number").fill("18091");

    await page.getByRole("button", { name: "Search for patient" }).click();

    // Make sure we have a results page with a single patient
    await expect(
      page.getByRole("heading", { name: "Patient Record" }),
    ).toBeVisible();
    await expect(page.getByText("Patient Name")).toBeVisible();
    await expect(page.getByText("WATERMELON SPROUT MCGEE")).toBeVisible();
    await expect(page.getByText("Patient Identifiers")).toBeVisible();
    await expect(page.getByText("MRN: 18091")).toBeVisible();
  });

  test("Query with multiple patients returned", async ({ page }) => {
    // Query for a patient with multiple results
    await page
      .getByLabel("Query", { exact: true })
      .selectOption("Chlamydia case investigation");
    await page.getByRole("button", { name: "Advanced" }).click();
    await page
      .getByLabel("FHIR Server (QHIN)", { exact: true })
      .selectOption("JMC Meld: Direct");
    await page.getByLabel("Last Name").fill("JMC");

    await page.getByRole("button", { name: "Search for patient" }).click();
    // Make sure all the elements for the multiple patients view appear
    await expect(
      page.getByRole("heading", { name: "Select a patient" }),
    ).toBeVisible();
    // Check that there is a Table element with the correct headers
    await expect(page.locator("thead").locator("tr")).toHaveText(
      "NameDOBContactAddressMRNActions",
    );

    // Check that there are multiple rows in the table
    await expect(page.locator("tbody").locator("tr")).toHaveCount(10);

    // Click on the first patient's "Select patient" button
    await page.locator(':nth-match(:text("Select patient"), 1)').click();

    // Make sure we have a results page with a single patient & appropriate back buttons
    await expect(
      page.getByRole("heading", { name: "Patient Record" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "New patient search" }),
    ).toBeVisible();

    await page.getByRole("button", { name: "New patient search" }).click();
    await expect(
      page.getByRole("heading", { name: "Search for a Patient", exact: true }),
    ).toBeVisible();
  });
});
