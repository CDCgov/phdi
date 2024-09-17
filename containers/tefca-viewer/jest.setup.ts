import "@testing-library/jest-dom";
import { toHaveNoViolations } from "jest-axe";
import * as matchers from "jest-extended";

expect.extend(toHaveNoViolations);
expect.extend(matchers);
