import React from "react";
import { removeHtmlElements } from "@/app/services/formatService";
import { DisplayDataProps } from "@/app/DataDisplay";

export interface PathMappings {
  [key: string]: string;
}

export interface ColumnInfoInput {
  columnName: string;
  infoPath?: string;
  value?: string;
  className?: string;
  hiddenBaseText?: string;
  applyToValue?: "toSentenceCase" | "formatDate";
}

export interface CompleteData {
  availableData: DisplayDataProps[];
  unavailableData: DisplayDataProps[];
}

export const noData = (
  <span className="no-data text-italic text-base">No data</span>
);

/**
 * Evaluates the provided display data to determine availability.
 * @param data - An array of display data items to be evaluated.
 * @returns - An object containing arrays of available and unavailable display data items.
 */
export const evaluateData = (data: DisplayDataProps[]): CompleteData => {
  let availableData: DisplayDataProps[] = [];
  let unavailableData: DisplayDataProps[] = [];
  data.forEach((item) => {
    if (!isDataAvailable(item)) {
      unavailableData.push(item);
    } else {
      availableData.push(item);
    }
  });
  return { availableData: availableData, unavailableData: unavailableData };
};

/**
 * Checks if data is available based on DisplayDataProps value. Also filters out terms that indicate info is unavailable.
 * @param item - The DisplayDataProps object to check for availability.
 * @returns - Returns true if data is available, false otherwise.
 */
export const isDataAvailable = (item: DisplayDataProps): Boolean => {
  if (!item.value || (Array.isArray(item.value) && item.value.length === 0))
    return false;
  const unavailableTerms = [
    "Not on file",
    "Not on file documented in this encounter",
    "Unknown",
    "Unknown if ever smoked",
    "Tobacco smoking consumption unknown",
    "Do not know",
    "No history of present illness information available",
  ];
  for (const i in unavailableTerms) {
    if (removeHtmlElements(`${item.value}`).trim() === unavailableTerms[i]) {
      return false;
    }
  }
  return true;
};
