"use strict";
var __importDefault =
  (this && this.__importDefault) ||
  function (mod) {
    return mod && mod.__esModule ? mod : { default: mod };
  };
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importDefault(require("react"));
const react_uswds_1 = require("@trussworks/react-uswds");
const formatService_1 = require("../services/formatService");
/**
 * Functional component for an accordion container displaying various sections of eCR information.
 * @param props - Props containing FHIR bundle and path mappings.
 * @param props.accordionItems - The list of accordion items.
 * @returns The JSX element representing the accordion container.
 */
const AccordionContainer = ({ accordionItems }) => {
  //Add id, adjust title
  const items = accordionItems.map((item, index) => {
    let formattedTitle = (0, formatService_1.formatString)(`${item["title"]}`);
    return Object.assign(Object.assign({}, item), {
      id: `${formattedTitle}_${index + 1}`,
      title: react_1.default.createElement(
        "span",
        { id: formattedTitle },
        item["title"],
      ),
    });
  });
  return react_1.default.createElement(react_uswds_1.Accordion, {
    className: "info-container",
    items: items,
    multiselectable: true,
  });
};
exports.default = AccordionContainer;
