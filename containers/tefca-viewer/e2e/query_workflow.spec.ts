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
      page.getByRole("heading", { name: "Case investigation made easier" }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "What is it?" }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "How does it work?" }),
    ).toBeVisible();

    // Check that interactable elements are present (TryTEFCA header and Get Started)
    await expect(
      page.getByRole("link", { name: "TryTEFCA Viewer" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Get Started" }),
    ).toBeVisible();
  });

  test("successful user query: the quest for watermelon mcgee", async ({
    page,
  }) => {
    await page.getByRole("button", { name: "Get Started" }).click();

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
    await page.getByRole("button", { name: "Get Started" }).click();

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