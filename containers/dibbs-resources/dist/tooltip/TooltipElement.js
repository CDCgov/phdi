"use strict";
var __rest =
  (this && this.__rest) ||
  function (s, e) {
    var t = {};
    for (var p in s)
      if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
      for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
        if (
          e.indexOf(p[i]) < 0 &&
          Object.prototype.propertyIsEnumerable.call(s, p[i])
        )
          t[p[i]] = s[p[i]];
      }
    return t;
  };
var __importDefault =
  (this && this.__importDefault) ||
  function (mod) {
    return mod && mod.__esModule ? mod : { default: mod };
  };
Object.defineProperty(exports, "__esModule", { value: true });
exports.TooltipElement = exports.TooltipDiv = void 0;
const react_1 = __importDefault(require("react"));
const react_uswds_1 = require("@trussworks/react-uswds");
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
const CustomDivForwardRef = (_a, ref) => {
  var { className, children } = _a,
    tooltipProps = __rest(_a, ["className", "children"]);
  return react_1.default.createElement(
    "div",
    Object.assign({ ref: ref, className: className }, tooltipProps),
    children,
  );
};
exports.TooltipDiv = react_1.default.forwardRef(CustomDivForwardRef);
/**
 * Creates a tooltip-wrapped element if a tooltip text is provided, or returns the content directly otherwise.
 * The tooltip is only applied when the `tooltip` parameter is not null or undefined. If the tooltip text
 * is less than 100 characters, a specific class `short-tooltip` is added to style the tooltip differently.
 * @param content - The properties object for tooltips.
 * @param content.content - The content to be displayed, which can be any valid React node or text
 * @param content.tooltip - The text for the tooltip. If this is provided, the content will be wrapped in a tooltip.
 * @returns A React JSX element containing either the plain content or content wrapped in a tooltip, depending on the tooltip parameter.
 */
const TooltipElement = ({ content, tooltip }) => {
  return tooltip
    ? react_1.default.createElement(
        react_uswds_1.Tooltip,
        {
          label: tooltip,
          asCustom: exports.TooltipDiv,
          className: `usa-tooltip${tooltip.length < 100 ? " short-tooltip" : ""}`,
        },
        content,
      )
    : react_1.default.createElement(react_1.default.Fragment, null, content);
};
exports.TooltipElement = TooltipElement;
