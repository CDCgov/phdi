import {
  ValueSetItem,
  ValueSetType,
  valueSetTypeToClincalServiceTypeMap,
} from "@/app/constants";

export type GroupedValueSet = {
  valueSetName: string;
  author: string;
  system: string;
  items: ValueSetItem[];
};

/**
 * Helper function that takes an array of value set items and groups them using
 * a combination of the value set name, author, and system to create a unique
 * grouping of items. These groups are displayed as individual accordions on
 * the customize query page
 * @param valueSetsToGroup - an array of value sets to group
 * @returns - a dictionary of value sets, where the index are the unique combinations
 * of valueSetName:author:system and the values are all the value set items that
 * share those identifiers in common, structed as a GroupedValueSet
 */
function groupValueSetsByNameAuthorSystem(valueSetsToGroup: ValueSetItem[]) {
  const results = valueSetsToGroup.reduce(
    (acc, row) => {
      // Check if both author and code_system are defined
      const author = row?.author;
      const system = row?.system;
      const valueSetName = row?.valueSetName;
      if (!author || !system || !valueSetName) {
        console.warn(
          `Skipping malformed row: Missing author (${author}) or system (${system}) for code (${row?.code})`,
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
    {} as Record<string, GroupedValueSet>,
  );

  return results;
}

export type TypeIndexedGroupedValueSetDictionary = {
  [valueSetType in ValueSetType]: {
    [vsNameAuthorSystem: string]: GroupedValueSet;
  };
};

/**
 * A helper function that takes all the ValueSetItems for a given condition,
 * parses them based on clinical code, and sorts them into the
 * ValueSetType buckets for the condition. The result is an dictionary
 * object, with index of labs, conditions, medications that we display on the
 * customize query page, where each dictionary is a separate accordion grouping
 * of ValueSetItems that users can select to filter their custom queries with
 * @param  vsItemArray - an array of ValueSetItems to group
 * @returns A dictionary of
 * dictionaries, where the first index is the ValueSetType, which indexes a
 * dictionary of GroupedValueSets. The subdictionary is indexed by
 * valueSetName:author:system
 */
export function mapValueSetItemsToValueSetTypes(vsItemArray: ValueSetItem[]) {
  const valueSetsByNameAuthorSystem =
    groupValueSetsByNameAuthorSystem(vsItemArray);
  const results: {
    [vsType in ValueSetType]: { [vsNameAuthorSystem: string]: GroupedValueSet };
  } = {
    labs: {},
    conditions: {},
    medications: {},
  };

  Object.entries(valueSetsByNameAuthorSystem).map(
    ([nameAuthorSystem, groupedValueSet]) => {
      const mappedSets = mapValueSetsToValueSetType(groupedValueSet.items);

      Object.entries(mappedSets).forEach(([valueSetTypeKey, items]) => {
        // the sieving function below accounts for the case that a GroupedValueSet
        // might have items that belong to more than one ValueSetType.
        // In practice, this doesn't occur very often / will result in empty
        // GroupedValueSets (ie the groupings on the other tabs) that we don't
        // want to display, so we should filter those out.
        if (items.length > 0) {
          results[valueSetTypeKey as ValueSetType][nameAuthorSystem] = {
            ...groupedValueSet,
            items: items,
          };
        }
      });
    },
  );

  return results;
}

/**
 * Helper function to map an array of value set items into their lab, medication,
 * condition buckets to be displayed on the customize query page
 * @param vsItems A list of value sets mapped from DB rows.
 * @returns Dict of list of rows containing only the predicate service type
 * mapped to one of "labs", "medications", or "conditions".
 */
export const mapValueSetsToValueSetType = (vsItems: ValueSetItem[]) => {
  const results: { [vsType in ValueSetType]: ValueSetItem[] } = {
    labs: [],
    medications: [],
    conditions: [],
  };
  (
    Object.keys(valueSetTypeToClincalServiceTypeMap) as Array<ValueSetType>
  ).forEach((vsType) => {
    const itemsToInclude = vsItems.filter((vs) => {
      return valueSetTypeToClincalServiceTypeMap[vsType].includes(
        vs.clinicalServiceType,
      );
    });
    results[vsType] = itemsToInclude;
  });

  return results;
};
