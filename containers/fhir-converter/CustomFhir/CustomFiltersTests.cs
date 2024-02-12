using Microsoft.Health.Fhir.Liquid.Converter;

namespace CustomFhir;

public class CustomFilterTests
{
    [Fact]
    public void ToHtmlString_String_ReturnsSameString()
    {
        var actual = Filters.ToHtmlString("Doc");
        Assert.Equal("Doc", actual);
    }
}