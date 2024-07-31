import { formatString } from "../formatService";

describe("formatString", () => {
  it("should convert string to lowercase", () => {
    expect(formatString("HELLO")).toBe("hello");
  });

  it("should replace spaces with hyphens", () => {
    expect(formatString("hello world")).toBe("hello-world");
  });

  it("should remove special characters", () => {
    expect(formatString("Hello@World!")).toBe("helloworld");
  });
});
