"use client";
import { createContext, ReactNode, useState } from "react";
import React from "react";
import classNames from "classnames";

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
 * @param root0
 * @param root0.children
 */
export function DataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<any | null>(null);

  return (
    <DataContext.Provider value={{ data, setData }}>
      {children}
    </DataContext.Provider>
  );
}
