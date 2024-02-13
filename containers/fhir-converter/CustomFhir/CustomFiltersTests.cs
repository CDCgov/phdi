using Microsoft.Health.Fhir.Liquid.Converter;
using System.Collections.Generic;

namespace CustomFhir;

public class CustomFilterTests
{
    [Fact]
    public void ToHtmlString_String_ReturnsSameString()
    {
        var actual = Filters.ToHtmlString("Doc");
        Assert.Equal("Doc", actual);
    }

    [Fact]
    public void ToHtmlString_StringList_ReturnsCharacters()
    {
        var strList = new List<string>(){"Race", "car"};
        Console.WriteLine(strList);
        var actual = Filters.ToHtmlString(strList);
        Assert.Equal("Racecar", actual);
    }
}