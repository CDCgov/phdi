import { Bundle } from "fhir/r4";

export class BundleClass implements Bundle {
  resourceType: "Bundle";
  type: "searchset" = "searchset";
  total?: number;
  entry?: Array<{ resource: any }>;

  constructor({
    resourceType = "Bundle",
    type = "searchset",
    total = 0,
    entry = [],
  }: {
    resourceType?: "Bundle";
    type?: "searchset";
    total?: number;
    entry?: Array<{ resource: any }>;
  } = {}) {
    this.resourceType = resourceType;
    this.type = type;
    this.total = total;
    this.entry = entry;
  }
}
