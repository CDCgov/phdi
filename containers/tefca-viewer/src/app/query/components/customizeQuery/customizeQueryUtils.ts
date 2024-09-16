import { ValueSetItem, ValueSetType } from "@/app/constants";

export type GroupedValueSet = {
  valueSetName: string;
  author: string;
  system: string;
  items: ValueSetItem[];
};
export type GroupedValueSetDictionary = {
  [VSNameAuthorSystem: string]: GroupedValueSet;
};

function groupValueSetsByNameAuthorSystem(valueSetsToGroup: ValueSetItem[]) {
  const results: GroupedValueSetDictionary = valueSetsToGroup.reduce(
    (acc, row) => {
      // Check if both author and code_system are defined
      const author = row?.author;
      const system = row?.system;
      const valueSetName = row?.valueSetName;
      if (!author || !system || !valueSetName) {
        console.warn(
          `Skipping malformed row: Missing author (${author}) or system (${system}) for code (${row?.code})`
        );
        return acc;
      }

      const groupKey = `${valueSetName}:${author}:${system}`;
      if (!acc[groupKey]) {
        acc[groupKey] = {
          valueSetName: valueSetName,
          author: author,
          system: system,
          items: [],
        };
      }
      acc[groupKey].items.push({
        code: row["code"],
        display: row["display"],
        system: row["system"],
        include: row["include"],
        author: row["author"],
        valueSetName: row["valueSetName"],
        clinicalServiceType: row["clinicalServiceType"],
      });
      return acc;
    },
    {} as Record<string, GroupedValueSet>
  );

  return results;
}

export type TypeIndexedGroupedValueSetDictionary = {
  [valueSetType in ValueSetType]: GroupedValueSetDictionary;
};

export function mapGroupedValueSetsToValueSetTypes(
  vsItemArray: ValueSetItem[]
) {
  const valueSetsByNameAuthorSystem =
    groupValueSetsByNameAuthorSystem(vsItemArray);
  const results: { [vsType in ValueSetType]: GroupedValueSetDictionary } = {
    labs: {},
    conditions: {},
    medications: {},
  };

  Object.entries(valueSetsByNameAuthorSystem).map(
    ([nameAuthorSystem, groupedValueSet]) => {
      const {
        labs: labItems,
        conditions: conditionItems,
        medications: medicationItems,
      } = filterValueSetsSync(groupedValueSet.items);

      if (labItems.length > 0) {
        results["labs"][nameAuthorSystem] = {
          ...groupedValueSet,
          items: labItems,
        };
      }
      if (conditionItems.length > 0) {
        results["conditions"][nameAuthorSystem] = {
          ...groupedValueSet,
          items: conditionItems,
        };
      }
      if (medicationItems.length > 0) {
        results["medications"][nameAuthorSystem] = {
          ...groupedValueSet,
          items: medicationItems,
        };
      }
    }
  );

  return results;
}

/**
 * Helper function to filter the valueset-mapped rows of results returned from
 * the DB for particular types of related clinical services.
 * @param vsItems A list of value sets mapped from DB rows.
 * @returns Dict of list of rows containing only the predicate service type mapped to
 * one of "labs", "medications", or "conditions".
 */
export const filterValueSetsSync = (vsItems: ValueSetItem[]) => {
  const valueSetSieve = {
    labs: ["ostc", "lotc", "lrtc"],
    medications: ["mrtc"],
    conditions: ["dxtc", "sdtc"],
  };
  const results: { [vsType in ValueSetType]: ValueSetItem[] } = {
    labs: [],
    medications: [],
    conditions: [],
  };

  (Object.keys(valueSetSieve) as Array<keyof typeof valueSetSieve>).forEach(
    (vsType) => {
      const itemsToInclude = vsItems.filter((vs) => {
        return valueSetSieve[vsType].includes(vs.clinicalServiceType);
      });
      results[vsType] = itemsToInclude;
    }
  );

  return results;
};
