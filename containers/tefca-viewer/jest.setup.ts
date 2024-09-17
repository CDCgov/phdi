import "@testing-library/jest-dom";
import { toHaveNoViolations } from "jest-axe";
import * as matchers from "jest-extended";

// import { TextEncoder } from "util";
// global.TextEncoder = TextEncoder;

// Uncomment and import the TextDecoder if interceptor parsing becomes a problem
// global.TextDecoder = TextDecoder;

expect.extend(toHaveNoViolations);
expect.extend(matchers);
