import { ValueSetItem, ValueSetType } from "@/app/constants";

export type GroupedValueSet = {
  valueSetName: string;
  author: string;
  system: string;
  items: ValueSetItem[];
};
