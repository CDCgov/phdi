import React from "react";
type CustomDivProps = React.PropsWithChildren<{
  className?: string;
}> &
  JSX.IntrinsicElements["div"] &
  React.RefAttributes<HTMLDivElement>;
export declare const TooltipDiv: React.ForwardRefExoticComponent<
  Omit<CustomDivProps, "ref"> & React.RefAttributes<HTMLDivElement>
>;
interface TooltipProps {
  content?: string;
  tooltip?: string;
}
/**
 * Creates a tooltip-wrapped element if a tooltip text is provided, or returns the content directly otherwise.
 * The tooltip is only applied when the `tooltip` parameter is not null or undefined. If the tooltip text
 * is less than 100 characters, a specific class `short-tooltip` is added to style the tooltip differently.
 * @param content - The properties object for tooltips.
 * @param content.content - The content to be displayed, which can be any valid React node or text
 * @param content.tooltip - The text for the tooltip. If this is provided, the content will be wrapped in a tooltip.
 * @returns A React JSX element containing either the plain content or content wrapped in a tooltip, depending on the tooltip parameter.
 */
export declare const TooltipElement: ({
  content,
  tooltip,
}: TooltipProps) => React.JSX.Element;
export {};
