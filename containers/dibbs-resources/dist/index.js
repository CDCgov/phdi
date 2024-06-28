"use strict";
var __importDefault =
  (this && this.__importDefault) ||
  function (mod) {
    return mod && mod.__esModule ? mod : { default: mod };
  };
Object.defineProperty(exports, "__esModule", { value: true });
exports.AccordionContainer =
  exports.removeHtmlElements =
  exports.addCaptionToTable =
  exports.toSentenceCase =
  exports.truncateLabNameWholeWord =
  exports.extractNumbersAndPeriods =
  exports.formatTablesToJSON =
  exports.formatString =
  exports.formatVitals =
  exports.formatStartEndDateTime =
  exports.formatPhoneNumber =
  exports.formatDate =
  exports.formatDateTime =
  exports.formatAddress =
  exports.formatName =
  exports.TooltipElement =
    void 0;
var TooltipElement_1 = require("./tooltip/TooltipElement");
Object.defineProperty(exports, "TooltipElement", {
  enumerable: true,
  get: function () {
    return TooltipElement_1.TooltipElement;
  },
});
var formatService_1 = require("./services/formatService");
Object.defineProperty(exports, "formatName", {
  enumerable: true,
  get: function () {
    return formatService_1.formatName;
  },
});
Object.defineProperty(exports, "formatAddress", {
  enumerable: true,
  get: function () {
    return formatService_1.formatAddress;
  },
});
Object.defineProperty(exports, "formatDateTime", {
  enumerable: true,
  get: function () {
    return formatService_1.formatDateTime;
  },
});
Object.defineProperty(exports, "formatDate", {
  enumerable: true,
  get: function () {
    return formatService_1.formatDate;
  },
});
Object.defineProperty(exports, "formatPhoneNumber", {
  enumerable: true,
  get: function () {
    return formatService_1.formatPhoneNumber;
  },
});
Object.defineProperty(exports, "formatStartEndDateTime", {
  enumerable: true,
  get: function () {
    return formatService_1.formatStartEndDateTime;
  },
});
Object.defineProperty(exports, "formatVitals", {
  enumerable: true,
  get: function () {
    return formatService_1.formatVitals;
  },
});
Object.defineProperty(exports, "formatString", {
  enumerable: true,
  get: function () {
    return formatService_1.formatString;
  },
});
Object.defineProperty(exports, "formatTablesToJSON", {
  enumerable: true,
  get: function () {
    return formatService_1.formatTablesToJSON;
  },
});
Object.defineProperty(exports, "extractNumbersAndPeriods", {
  enumerable: true,
  get: function () {
    return formatService_1.extractNumbersAndPeriods;
  },
});
Object.defineProperty(exports, "truncateLabNameWholeWord", {
  enumerable: true,
  get: function () {
    return formatService_1.truncateLabNameWholeWord;
  },
});
Object.defineProperty(exports, "toSentenceCase", {
  enumerable: true,
  get: function () {
    return formatService_1.toSentenceCase;
  },
});
Object.defineProperty(exports, "addCaptionToTable", {
  enumerable: true,
  get: function () {
    return formatService_1.addCaptionToTable;
  },
});
Object.defineProperty(exports, "removeHtmlElements", {
  enumerable: true,
  get: function () {
    return formatService_1.removeHtmlElements;
  },
});
var AccordionContainer_1 = require("./accordion/AccordionContainer");
Object.defineProperty(exports, "AccordionContainer", {
  enumerable: true,
  get: function () {
    return __importDefault(AccordionContainer_1).default;
  },
});
