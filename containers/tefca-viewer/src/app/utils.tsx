"use client";
import { createContext, ReactNode, useState } from "react";
import React from "react";
import classNames from "classnames";

/**
 * @todo Add country code form box on search form
 * @todo Update documentation here once that's done to reflect switch
 * logic of country code
 *
 * Helper function to strip out non-digit characters from a phone number
 * entered into the search tool. Right now, we're not going to worry about
 * country code or international numbers, so we'll just make an MVP
 * assumption of 10 regular digits.
 * @param givenPhone The original phone number the user typed.
 * @returns The phone number as a pure digit string. If the cleaned number
 * is fewer than 10 digits, just return the original.
 */
export function FormatPhoneAsDigits(givenPhone: string) {
  // Start by getting rid of all existing separators for a clean slate
  const newPhone: string = givenPhone.replace(/\D/g, "");
  if (newPhone.length != 10) {
    return givenPhone;
  }
  return newPhone;
}

export interface DisplayData {
  title: string;
  value?: string | React.JSX.Element | React.JSX.Element[];
}

/**
 * Functional component for displaying data.
 * @param props - Props for the component.
 * @param props.item - The display data item to be rendered.
 * @param [props.className] - Additional class name for styling purposes.
 * @returns - A React element representing the display of data.
 */
export const DataDisplay: React.FC<{
  item: DisplayData;
  className?: string;
}> = ({
  item,
  className,
}: {
  item: DisplayData;
  className?: string;
}): React.JSX.Element => {
  return (
    <div>
      <div className="grid-row">
        <div className="data-title">{item.title}</div>
        <div
          className={classNames("grid-col-auto maxw7 text-pre-line", className)}
        >
          {item.value}
        </div>
      </div>
      <div className={"section__line_gray"} />
    </div>
  );
};

interface DataContextValue {
  data: any; // You can define a specific data type here
  setData: (data: any) => void;
}

const DataContext = createContext<DataContextValue | undefined>(undefined);

/**
 *
 * @param root0 - Children
 * @param root0.children - Children
 * @returns - The data provider component.
 */
export function DataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<any | null>(null);

  return (
    <DataContext.Provider value={{ data, setData }}>
      {children}
    </DataContext.Provider>
  );
}
