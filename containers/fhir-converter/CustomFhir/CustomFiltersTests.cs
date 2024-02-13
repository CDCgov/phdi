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

    // from 020e83d2-a1ca-4056-bc9f-6cffe8609e99 Active Problems
    // <text>
    // <table>
    // <colgroup>
    //     <col width="75%"/>
    //     <col width="25%"/>
    // </colgroup>
    // <thead>
    //     <tr>
    //         <th>Active Problems</th>
    //         <th>Noted Date</th>
    //     </tr>
    // </thead>
    // <tbody>
    //     <tr ID="problem13" styleCode="xRowNormal">
    //         <td ID="problem13name">Parkinson's syndrome</td>
    //         <td>7/25/22</td>
    //     </tr>
    //     <tr ID="problem12" styleCode="xRowAlt">
    //         <td ID="problem12name">Essential hypertension</td>
    //         <td>7/21/22</td>
    //     </tr>
    // </tbody>
    // </table>
    // <footnote ID="subTitle11" styleCode="xSectionSubTitle">documented as of this encounter (statuses as of 07/25/2022)</footnote>
    // </text>
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
        Assert.Equal("<table><thead><tr><th>Active Problems</th><th>Noted Date</th></tr></thead><tbody><tr><td>Parkinson's syndrome</td><td>7/25/22</td></tr><tr><td>Essential hypertension</td><td>7/21/22</td></tr></tbody></table>documented as of this encounter (statuses as of 07/25/2022)", actual);
    }
}