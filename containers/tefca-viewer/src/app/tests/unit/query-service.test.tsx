import { GetPhoneQueryFormats } from "@/app/query-service";

describe("GetPhoneQueryFormats", () => {
  it("should fail gracefully on partial phone number inputs", async () => {
    const partialPhone = "456 7890";
    const expectedResult = ["456+7890"];
    expect(await GetPhoneQueryFormats(partialPhone)).toEqual(expectedResult);
  });
  it("should fail gracefully on given phones with separators remaining", async () => {
    const phoneWithStuff = "+44.202.456.7890";
    const expectedResult = ["+44.202.456.7890"];
    expect(await GetPhoneQueryFormats(phoneWithStuff)).toEqual(expectedResult);
  });
  it("should fully process ten-digit input strings", async () => {
    const inputPhone = "1234567890";
    const expectedResult = [
      "1234567890",
      "123-456-7890",
      "123+456+7890",
      "(123)+456+7890",
      "(123)-456-7890",
      "(123)456-7890",
      "1(123)456-7890",
    ];
    expect(await GetPhoneQueryFormats(inputPhone)).toEqual(expectedResult);
  });
});
