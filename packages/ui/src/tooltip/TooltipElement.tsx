import React from "react";
import { Tooltip } from "@trussworks/react-uswds";

type CustomDivProps = React.PropsWithChildren<{
  className?: string;
}> &
  React.JSX.IntrinsicElements["div"] &
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
const CustomDivForwardRef: React.ForwardRefRenderFunction<
  HTMLDivElement,
  CustomDivProps
> = ({ className, children, ...tooltipProps }: CustomDivProps, ref) => (
  <div ref={ref} className={className} {...tooltipProps}>
    {children}
  </div>
);
export const TooltipDiv = React.forwardRef(CustomDivForwardRef);

interface TooltipProps {
  content?: string;
  tooltip?: string;
}

/**
 * Creates a tooltip-wrapped element if a tooltip text is provided, or returns the content directly otherwise.
 * The tooltip is only applied when the `tooltip` parameter is not null or undefined. If the tooltip text
 * is less than 100 characters, a specific class `short-tooltip` is added to style the tooltip differently.
 * @param content - The content to be displayed, which can be any valid React node or text.
 * @param tooltip - The text for the tooltip. If this is provided, the content will be wrapped in a tooltip.
 * @returns A React JSX element containing either the plain content or content wrapped in a tooltip, depending on the tooltip parameter.
 */
export const TooltipElement = ({
  content,
  tooltip,
}: TooltipProps): React.JSX.Element => {
  return tooltip ? (
    <Tooltip
      label={tooltip}
      asCustom={TooltipDiv}
      className={`usa-tooltip${tooltip.length < 100 ? " short-tooltip" : ""}`}
    >
      {content}
    </Tooltip>
  ) : (
    <>{content}</>
  );
};
