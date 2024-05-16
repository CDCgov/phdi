import React from "react";
import { removeHtmlElements } from "@/app/services/formatService";
import { Tooltip } from "@trussworks/react-uswds";
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
