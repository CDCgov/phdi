import "@testing-library/jest-dom";
import { toHaveNoViolations } from "jest-axe";
import * as matchers from "jest-extended";
import { TextEncoder } from "util";

global.TextEncoder = TextEncoder;

expect.extend(toHaveNoViolations);
expect.extend(matchers);
