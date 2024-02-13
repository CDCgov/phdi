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
    public void ToHtmlString_ObjectList_ReturnsStrings()
    {
        var strList = new List<object>(){"Race", "car"};
        var actual = Filters.ToHtmlString(strList);
        Assert.Equal("Racecar", actual);
    }

    [Fact]
    public void ToHtmlString_StringObjectDictionaryUnderscore_ReturnsOnlyUnderscoreString()
    {
        var strList = new Dictionary<string, object>(){
            {"_", "car"},
            {"/nSun", "flower"}
        };
        var actual = Filters.ToHtmlString(strList);
        Assert.Equal("car", actual);
    }

    [Fact]
    public void ToHtmlString_StringObjectDictionaryBr_ReturnsOnlyBR()
    {
        var strList = new Dictionary<string, object>(){
            {"br", ""},
            {"/nSun", "flower"}
        };
        var actual = Filters.ToHtmlString(strList);
        Assert.Equal("<br>", actual);
    }
}