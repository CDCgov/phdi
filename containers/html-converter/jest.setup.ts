import '@testing-library/jest-dom'
import {toHaveNoViolations} from 'jest-axe'
import {expect} from "@jest/globals";

expect.extend(toHaveNoViolations);
