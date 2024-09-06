import { NextResponse } from "next/server";
import pgPromise from "pg-promise";

interface BundleMetadata {
  last_name: string;
  first_name: string;
  birth_date: string;
  data_source: string;
  reportable_condition: string;
  rule_summary: string;
  report_date: string;
}

/**
 * Saves a FHIR bundle metadata to a postgres database.
 * @async
 * @function saveToS3
 * @param metadata - The FHIR bundle metadata to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle metadata is successfully saved to postgres.
 * @throws {Error} Throws an error if the FHIR bundle metadata cannot be saved to postgress.
 */
export const saveToPostgres = async (
  metadata: BundleMetadata,
  ecrId: string,
) => {
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);

  const { ParameterizedQuery: PQ } = pgPromise;
  const addMetadata = new PQ({
    text: "INSERT INTO fhir_metadata (ecr_id,patient_name_last,patient_name_first,patient_birth_date,data_source,reportable_condition,rule_summary,report_date) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING ecr_id",
    values: [
      ecrId,
      metadata.first_name,
      metadata.last_name,
      metadata.birth_date,
      "DB",
      metadata.reportable_condition,
      metadata.rule_summary,
      metadata.report_date,
    ],
  });

  try {
    const saveECR = await database.one(addMetadata);

    return NextResponse.json(
      { message: "Success. Saved metadata to database: " + saveECR.ecr_id },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("Error inserting metadata to database:", error);
    return NextResponse.json(
      { message: "Failed to insert metadata to database. " + error.message },
      { status: 400 },
    );
  }
};
