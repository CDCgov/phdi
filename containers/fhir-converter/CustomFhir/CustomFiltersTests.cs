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
        var strList = new List<object>() { "Race", "car" };
        var actual = Filters.ToHtmlString(strList);
        Assert.Equal("Racecar", actual);
    }

    [Fact]
    public void ToHtmlString_StringObjectDictionaryUnderscore_ReturnsOnlyUnderscoreString()
    {
        var underscoreDict = new Dictionary<string, object>(){
            {"_", "car"},
            {"/nSun", "flower"}
        };
        var actual = Filters.ToHtmlString(underscoreDict);
        Assert.Equal("car", actual);
    }

    [Fact]
    public void ToHtmlString_StringObjectDictionaryBr_ReturnsOnlyBR()
    {
        var brDict = new Dictionary<string, object>(){
            {"br", ""},
            {"/nSun", "flower"}
        };
        var actual = Filters.ToHtmlString(brDict);
        Assert.Equal("<br>", actual);
    }

    [Fact]
    public void ToHtmlString_StringObjectDictionaryAnotherDictionary_ReturnsHTMLValues()
    {
        var underscoreDict = new Dictionary<string, object>(){
            {"_", "paragraph text"}
        };
        var dictDict = new Dictionary<string, object>(){
            {"p", underscoreDict},
            {"/nSun", "flower"}
        };
        var actual = Filters.ToHtmlString(dictDict);
        Assert.Equal("<p>paragraph text</p>", actual);
    }

    [Fact]
    public void ToHtmlString_StringObjectDictionaryList_ReturnsEachItemWithTags()
    {
        var strList = new List<object>() { "Race", "car" };
        var dictDict = new Dictionary<string, object>(){
            {"span", strList},
            {"/nSun", "flower"}
        };
        var actual = Filters.ToHtmlString(dictDict);
        Assert.Equal("<span>Race</span><span>car</span>", actual);
    }

    [Fact]
    public void ToHtmlString_ComplicatedExample_ReturnsString()
    {
        var footnote = new Dictionary<string, object>(){
            {"ID", "subTitle11"},
            {"styleCode", "xSectionSubTitle"},
            {"_", "documented as of this encounter (statuses as of 07/25/2022)"}
        };
        var tbodyTrTd12Column1 = new Dictionary<string, object>(){
            {"ID", "problem12name"},
            {"_", "Essential hypertension"},
        };
        var tbodyTrTd12 = new List<object>() { tbodyTrTd12Column1, "7/21/22" };
        var tbodyTr12 = new Dictionary<string, object>(){
            {"ID", "problem12"},
            {"styleCode", "xRowAlt"},
            {"td", tbodyTrTd12},
        };
        var tbodyTrTd13Column1 = new Dictionary<string, object>(){
            {"ID", "problem13name"},
            {"_", "Parkinson's syndrome"},
        };
        var tbodyTrTd13 = new List<object>() { tbodyTrTd13Column1, "7/25/22" };
        var tbodyTr13 = new Dictionary<string, object>(){
            {"ID", "problem13"},
            {"styleCode", "xRowNormal"},
            {"td", tbodyTrTd13},
        };
        var tbodyTrList = new List<object>() { tbodyTr13, tbodyTr12 };
        var tbody = new Dictionary<string, object>(){
            {"tr", tbodyTrList},
        };
        var theadTrTh = new List<object>() { "Active Problems", "Noted Date" };
        var theadTr = new Dictionary<string, object>(){
            {"th", theadTrTh},
        };
        var thead = new Dictionary<string, object>(){
            {"tr", theadTr},
        };
        var col = new Dictionary<string, object>(){
            {"width", "50%"},
        };
        var colList = new List<object>() { col, col };
        var colGroup = new Dictionary<string, object>(){
            {"col", colList},
        };
        var table = new Dictionary<string, object>(){
            {"colgroup", colGroup},
            {"thead", thead},
            {"tbody", tbody}
        };
        var completeDict = new Dictionary<string, object>(){
            {"table", table},
            {"footnote", footnote}
        };

        var actual = Filters.ToHtmlString(completeDict);
        Assert.Equal("<table><thead><tr><th>Active Problems</th><th>Noted Date</th></tr></thead><tbody><tr data-id='problem13'><td data-id='problem13name'>Parkinson's syndrome</td><td>7/25/22</td></tr><tr data-id='problem12'><td data-id='problem12name'>Essential hypertension</td><td>7/21/22</td></tr></tbody></table>documented as of this encounter (statuses as of 07/25/2022)", actual);
    }

    [Fact]
    public void ToHtmlString_ContainsListXmlTags_ReturnsReplacedTags()
    {
        var itemList = new List<object>(){
                "Recurrent GI bleed of unknown etiology; hypotension perhaps secondary to this but as likely secondary to polypharmacy.",
                "Acute on chronic anemia secondary to #1.",
                "Azotemia, acute renal failure with volume loss secondary to #1.",
                "Hyperkalemia secondary to #3 and on ACE and K+ supplement.",
                "Other chronic diagnoses as noted above, currently stable."
            };
        var list = new Dictionary<string, object>() {
                {"listType", "ordered"},
                {"item", itemList}
            };
        var complete = new Dictionary<string, object>() {
                {"list", list}
            };
        var actual = Filters.ToHtmlString(complete);
        Assert.Equal("<ul><li>Recurrent GI bleed of unknown etiology; hypotension perhaps secondary to this but as likely secondary to polypharmacy.</li><li>Acute on chronic anemia secondary to #1.</li><li>Azotemia, acute renal failure with volume loss secondary to #1.</li><li>Hyperkalemia secondary to #3 and on ACE and K+ supplement.</li><li>Other chronic diagnoses as noted above, currently stable.</li></ul>", actual);
    }


    [Fact]
    public void ToHtmlString_InvalidTags_ReturnsStringWithSpaces()
    {
        var raceString = new Dictionary<string, object>() {
                {"_", "two"},
            };
        var carString = new Dictionary<string, object>() {
                {"_", "words"},
            };
        var complete = new Dictionary<string, object>() {
                {"invalidTag", raceString},
                {"badTag", carString}

            };
        var actual = Filters.ToHtmlString(complete);
        Assert.Equal("two words", actual);
    }

    [Fact]
    public void GetLoincName_ValidLOINC_ReturnsName()
    {
        var loinc = "34565-2";
        var actual = Filters.GetLoincName(loinc);
        Assert.Equal("Vital signs, weight and height panel", actual);
    }
}