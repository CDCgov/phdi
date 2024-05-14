import React, { ReactNode, useEffect, useState } from "react";

import classNames from "classnames";

import { removeHtmlElements } from "@/app/services/formatService";
import { Button } from "@trussworks/react-uswds";
import { Tooltip } from "@trussworks/react-uswds";

export interface DisplayDataProps {
  title?: string;
  className?: string;
  toolTip?: string;
  value?: string | React.JSX.Element | React.JSX.Element[] | React.ReactNode;
  dividerLine?: boolean;
}

export interface PathMappings {
  [key: string]: string;
}

export interface ColumnInfoInput {
  columnName: string;
  infoPath?: string;
  value?: string;
  className?: string;
  hiddenBaseText?: string;
  applyToValue?: (value: any) => any;
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

/**
 * Functional component for displaying data.
 * @param props - Props for the component.
 * @param props.item - The display data item to be rendered.
 * @param [props.className] - Additional class name for styling purposes.
 * @returns - A React element representing the display of data.
 */
export const DataDisplay: React.FC<{
  item: DisplayDataProps;
  className?: string;
}> = ({
  item,
  className,
}: {
  item: DisplayDataProps;
  className?: string;
}): React.JSX.Element => {
  item.dividerLine =
    item.dividerLine == null || item.dividerLine == undefined
      ? true
      : item.dividerLine;
  return (
    <div>
      <div className="grid-row">
        <div className="data-title">
          {toolTipElement(item.title, item.toolTip)}
        </div>
        <div
          className={classNames(
            "grid-col-auto maxw7 text-pre-line",
            className,
            item.className ? item.className : "",
          )}
        >
          <FieldValue>{item.value}</FieldValue>
        </div>
      </div>
      {item.dividerLine ? <div className={"section__line_gray"} /> : ""}
    </div>
  );
};

/**
 * Functional component for displaying a value. If the value has a length greater than 500 characters, it will be split after 300 characters with a view more button to view the entire value.
 * @param value - props for the component
 * @param value.children - the value to be displayed in the value
 * @returns - A React element representing the display of the value
 */
const FieldValue: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const maxLength = 500;
  const cutLength = 300;
  const [hidden, setHidden] = useState(true);
  const [fieldValue, setFieldValue] = useState(children);
  const valueLength = getReactNodeLength(children);
  const cutField = trimField(children, cutLength, setHidden).value;
  useEffect(() => {
    if (valueLength > maxLength) {
      if (hidden) {
        setFieldValue(cutField);
      } else {
        setFieldValue(
          <>
            {children}&nbsp;
            <Button
              type={"button"}
              unstyled={true}
              onClick={() => setHidden(true)}
            >
              View less
            </Button>
          </>,
        );
      }
    }
  }, [hidden]);

  return fieldValue;
};

/**
 * Recursively determine the character length of a ReactNode
 * @param value - react node to be measured
 * @returns - the number of characters in the ReactNode
 */
const getReactNodeLength = (value: React.ReactNode): number => {
  if (typeof value === "string") {
    return value.length;
  } else if (Array.isArray(value)) {
    let count = 0;
    value.forEach((val) => (count += getReactNodeLength(val)));
    return count;
  } else if (React.isValidElement(value) && value.props.children) {
    return getReactNodeLength(value.props.children);
  }
  return 0;
};

/**
 * Create an element with `remainingLength` length followed by a view more button
 * @param value - the value that will be cut
 * @param remainingLength - the length of how long the returned element will be
 * @param setHidden - a function used to signify that the view more button has been clicked.
 * @returns - an object with the shortened value and the length left over.
 */
const trimField = (
  value: React.ReactNode,
  remainingLength: number,
  setHidden: (val: boolean) => void,
): { value: React.ReactNode; remainingLength: number } => {
  if (remainingLength < 1) {
    return { value: null, remainingLength };
  }
  if (typeof value === "string") {
    const cutString = value.substring(0, remainingLength);
    if (remainingLength - cutString.length === 0) {
      return {
        value: (
          <>
            {cutString}...&nbsp;
            <Button
              type={"button"}
              unstyled={true}
              onClick={() => setHidden(false)}
            >
              View more
            </Button>
          </>
        ),
        remainingLength: 0,
      };
    }
    return {
      value: cutString,
      remainingLength: remainingLength - cutString.length,
    };
  } else if (Array.isArray(value)) {
    let newValArr = [];
    for (let i = 0; i < value.length; i++) {
      let splitVal = trimField(value[i], remainingLength, setHidden);
      remainingLength = splitVal.remainingLength;
      newValArr.push(
        <React.Fragment key={`arr-${i}-${splitVal.value}`}>
          {splitVal.value}
        </React.Fragment>,
      );
    }
    return { value: newValArr, remainingLength: remainingLength };
  } else if (React.isValidElement(value) && value.props.children) {
    let childrenCopy: ReactNode;
    if (Array.isArray(value.props.children)) {
      childrenCopy = [...value.props.children];
    } else {
      childrenCopy = value.props.children;
    }
    let split = trimField(childrenCopy, remainingLength, setHidden);
    const newElement = React.cloneElement(
      value,
      { ...value.props },
      split.value,
    );
    return { value: newElement, remainingLength: split.remainingLength };
  }
  return { value, remainingLength: remainingLength };
};

type CustomDivProps = React.PropsWithChildren<{
  className?: string;
}> &
  JSX.IntrinsicElements["div"] &
  React.RefAttributes<HTMLDivElement>;

/**
 * `CustomDivForwardRef` is a React forward reference component that renders a div element
 *  with extended capabilities. This component supports all standard div properties along with
 *  additional features provided by `tooltipProps`.
 * @component
 * @param props - The props for the CustomDiv component.
 * @param props.className - CSS class to apply to the div element.
 * @param props.children - Child elements or content to be rendered within the div.
 * @param props.tooltipProps - Additional props to be spread into the div element, typically used for tooltip logic or styling.
 * @param ref - Ref forwarded to the div element.
 * @returns A React element representing a customizable div.
 */
export const CustomDivForwardRef: React.ForwardRefRenderFunction<
  HTMLDivElement,
  CustomDivProps
> = ({ className, children, ...tooltipProps }: CustomDivProps, ref) => (
  <div ref={ref} className={className} {...tooltipProps}>
    {children}
  </div>
);

export const TooltipDiv = React.forwardRef(CustomDivForwardRef);

/**
 * Creates a tooltip-wrapped element if a tooltip text is provided, or returns the content directly otherwise.
 * The tooltip is only applied when the `toolTip` parameter is not null or undefined. If the tooltip text
 * is less than 100 characters, a specific class `short-tooltip` is added to style the tooltip differently.
 * @param content - The content to be displayed, which can be any valid React node or text.
 * @param toolTip - The text for the tooltip. If this is provided, the content will be wrapped in a tooltip.
 * @returns A React JSX element containing either the plain content or content wrapped in a tooltip, depending on the tooltip parameter.
 */
export const toolTipElement = (
  content: string | undefined | null,
  toolTip: string | undefined | null,
): React.JSX.Element => {
  return toolTip ? (
    <Tooltip
      label={toolTip}
      asCustom={TooltipDiv}
      className={`usa-tooltip${toolTip.length < 100 ? " short-tooltip" : ""}`}
    >
      {content}
    </Tooltip>
  ) : (
    <>{content}</>
  );
};
