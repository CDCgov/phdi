export { TooltipElement } from "./tooltip/TooltipElement";
export type { Metadata, TableRow, TableJson } from "./services/formatService";
export {
  formatName,
  formatAddress,
  formatDateTime,
  formatDate,
  formatPhoneNumber,
  formatStartEndDateTime,
  formatVitals,
  formatString,
  formatTablesToJSON,
  extractNumbersAndPeriods,
  truncateLabNameWholeWord,
  toSentenceCase,
  addCaptionToTable,
  removeHtmlElements,
} from "./services/formatService";
export { default as AccordionContainer } from "./accordion/AccordionContainer";
