import "@testing-library/jest-dom";
import "cross-fetch/polyfill";
import { toHaveNoViolations } from "jest-axe";
import { TextEncoder, TextDecoder } from "util";
import * as matchers from "jest-extended";

expect.extend(toHaveNoViolations);
expect.extend(matchers);
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
