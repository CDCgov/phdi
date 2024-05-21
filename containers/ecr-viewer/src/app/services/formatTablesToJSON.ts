import { JSDOM } from "jsdom";

interface Metadata {
  [key: string]: string;
}

export interface TableRow {
  [key: string]: {
    value: any;
    metadata: Metadata;
  };
}

export interface TableJson {
  resultId?: string;
  resultName?: string;
  tables?: TableRow[][];
}

/**
 * Parses an HTML string containing tables or a list of tables and converts each table into a JSON array of objects.
 * Each <li> item represents a different lab result. The resulting JSON objects contain the data-id (Result ID)
 * and text content of the <li> items, along with an array of JSON representations of the tables contained within each <li> item.
 * @param htmlString - The HTML string containing tables to be parsed.
 * @returns - An array of JSON objects representing the list items and their tables from the HTML string.
 * @example @returns [{resultId: 'Result.123', resultName: 'foo', tables: [{}, {},...]}, ...]
 */
export const formatTablesToJSON = (htmlString: string): TableJson[] => {
  // const parser = new DOMParser();
  // const doc = parser.parseFromString(htmlString, "text/html");
  const doc = new JSDOM(htmlString).window.document;
  const jsonArray: any[] = [];
  const liArray = doc.querySelectorAll("li");
  if (liArray.length > 0) {
    liArray.forEach((li) => {
      const tables: any[] = [];
      const resultId = li.getAttribute("data-id");
      const resultName = li.childNodes[0].textContent?.trim() ?? "";
      li.querySelectorAll("table").forEach((table) => {
        tables.push(processTable(table));
      });
      jsonArray.push({ resultId, resultName, tables });
    });
  } else {
    doc.querySelectorAll("table").forEach((table) => {
      const resultName = table.caption?.textContent;
      const resultId = table.getAttribute("data-id") ?? undefined;
      jsonArray.push({ resultId, resultName, tables: [processTable(table)] });
    });
  }

  return jsonArray;
};

/**
 * Processes a single HTML table element, extracting data from rows and cells, and converts it into a JSON array of objects.
 * This function extracts data from <tr> and <td> elements within the provided table element.
 * The content of <th> elements is used as keys in the generated JSON objects.
 * @param table - The HTML table element to be processed.
 * @returns - An array of JSON objects representing the rows and cells of the table.
 */
function processTable(table: Element): TableRow[] {
  const jsonArray: any[] = [];
  const rows = table.querySelectorAll("tr");
  const keys: string[] = [];

  rows[0].querySelectorAll("th").forEach((header) => {
    keys.push(header.textContent?.trim() ?? "");
  });

  rows.forEach((row, rowIndex) => {
    // Skip the first row as it contains headers
    if (rowIndex === 0) return;

    const obj: TableRow = {};
    row.querySelectorAll("td").forEach((cell, cellIndex) => {
      const key = keys[cellIndex];

      const metaData: Metadata = {};
      const attributes = cell.attributes || [];
      for (const element of attributes) {
        const attrName = element.nodeName;
        const attrValue = element.nodeValue;
        if (attrName && attrValue) {
          metaData[attrName] = attrValue;
        }
      }
      obj[key] = {
        value: cell.textContent?.trim() ?? "",
        metadata: metaData,
      };
    });
    jsonArray.push(obj);
  });

  return jsonArray;
}
