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

    // Check that interactable elements are present (TEFCA header and Get Started)
    await expect(
      page.getByRole("link", { name: "TEFCA Viewer" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Go to the demo" }),
    ).toBeVisible();
  });

  // Check that the clickable logo is visible
  // test("clickable logo is visible", async ({ page }) => {
  //   await expect(
  //     page.locator('a[href="/tefca-viewer"] img[alt="DIBBs Logo"]'),
  //   ).toBeVisible();
  // });

  test("successful user query: the quest for watermelon mcgee", async ({
    page,
  }) => {
    await page.getByRole("button", { name: "Go to the demo" }).click();
    await page.getByRole("button", { name: "Next" }).click();

    // Check that the info alert is visible and contains the correct text
    const alert = page.locator(".custom-alert");
    await expect(alert).toBeVisible();
    await expect(alert).toHaveText(
      "This site is for demo purposes only. Please do not enter PII on this website.",
    );

    // Put in the search parameters for the elusive fruit person
    await page.getByLabel("First Name").fill("Watermelon");
    await page.getByLabel("Last Name").fill("McGee");
    await page
      .getByLabel("Use case", { exact: true })
      .selectOption("newborn-screening");
    await page.getByLabel("FHIR Server").selectOption("HELIOS Meld: Direct");

    await page.getByRole("button", { name: "Search for patient" }).click();

    // Make sure we have a results page with a single patient
    // Non-interactive 'div' elements in the table should be located by text
    await expect(
      page.getByRole("heading", { name: "Query Results" }),
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

    // Let's get a little schwifty: there are multiple possible resolutions for 'Observations',
    // so we can chain things to get the table header to make sure the accordion is open
    await expect(
      page
        .getByTestId("accordionItem_observations_2")
        .getByRole("heading", { name: "Observations" }),
    ).toBeVisible();
    // We can also just directly ask the page to find us filtered table rows
    await expect(page.locator("tbody").locator("tr")).toHaveCount(5);

    // Now let's use the return to search to go back to a blank form
    await page.getByRole("link", { name: "Return to search" }).click();
    await expect(
      page.getByRole("heading", { name: "Search for a Patient" }),
    ).toBeVisible();
  });

  test("unsuccessful user query: no patients", async ({ page }) => {
    await page.getByRole("button", { name: "Go to the demo" }).click();
    await page.getByRole("button", { name: "Next" }).click();

    await page.getByLabel("First Name").fill("Ellie");
    await page.getByLabel("Last Name").fill("Williams");
    await page.getByLabel("Date of Birth").fill("2030-07-07");
    await page.getByLabel("Medical Record Number").fill("TLOU1TLOU2");
    await page
      .getByLabel("Use case", { exact: true })
      .selectOption("social-determinants");
    await page.getByLabel("FHIR Server").selectOption("HELIOS Meld: Direct");
    await page.getByRole("button", { name: "Search for patient" }).click();

    // Better luck next time, user!
    await expect(
      page.getByRole("heading", { name: "No Patients Found" }),
    ).toBeVisible();
    await expect(page.getByText("There are no patient records")).toBeVisible();
    await page.getByRole("link", { name: "Search for a new patient" }).click();
    await expect(
      page.getByRole("heading", { name: "Search for a Patient" }),
    ).toBeVisible();
  });
});
