using System;
using System.Collections.Generic;
using System.Collections;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;
using Microsoft.VisualBasic.FileIO;
using DotLiquid.Util;

namespace Microsoft.Health.Fhir.Liquid.Converter
{
  /// <summary>
  /// Filters for conversion
  /// </summary>
  public partial class Filters
  {
    private static HashSet<string> supportedTags = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "br", "li", "ol", "p", "span", "table", "tbody", "td", "textarea", "th", "thead", "tr", "u", "ul", "paragraph", "caption" };
    private static Dictionary<string, string> replaceTags = new Dictionary<string, string>{
        {"list", "ul"},
        {"item", "li"},
        {"paragraph", "p"}
    };
    private static Dictionary<string, string>? loincDict;

    // Items from the filter could be arrays or objects, process them to be the same
    private static List<Dictionary<string, object>> ProcessItem(object item)
    {
      if (item is Dictionary<string, object> dict)
      {
        return new List<Dictionary<string, object>> { dict };
      }
      else if (item is IEnumerable<object> collection)
      {
        return collection.Cast<Dictionary<string, object>>().ToList();
      }
      else if (item is IEnumerable<Dictionary<string, object>> collectionTwo)
      {
        return collectionTwo.ToList();
      }
      return new List<Dictionary<string, object>>();
    }

    /// <summary>
    /// Drills down into an object representing nested XML elements, by the given keys.
    /// </summary>
    /// <param name="item">The object to drill down into.</param>
    /// <param name="keys">The keys to drill down by.</param>
    /// <returns>The result of drilling down, which can be a list of dictionaries, or null if the item is null or the key does not exist.</returns>
    private static List<Dictionary<string, object>>? DrillDown(IDictionary<string, object> item, List<string> keys)
    {
      if (keys.Count == 0)
      {
        return ProcessItem(item);
      }

      string key = keys.Shift();

      if (item.TryGetValue(key, out object? val) && keys.Count > 0)
      {
        return DrillDown(ProcessItem(val), keys);
      }
      else if (val != null && keys.Count == 0)
      {
        return ProcessItem(val);
      }

      return null;
    }

    /// <summary>
    ///  Drills down into a list of objects representing nested XML elements, by the given keys.
    /// </summary>
    /// <param name="items">The list of objects to drill down into.</param>
    /// <param name="keys">The keys to drill down by.</param>
    /// <returns>The result of drilling down, which can be a list of dictionaries, or null if the items is null or empty, or the key does not exist.</returns>
    private static List<Dictionary<string, object>>? DrillDown(IList<Dictionary<string, object>> items, List<string> keys)
    {
      if (keys.Count == 0)
      {
        return (List<Dictionary<string, object>>)items;
      }

      string key = keys.Shift();

      if (items.Count != 0)
      {
        var result = new List<Dictionary<string, object>>();

        foreach (var item in items)
        {
          if (item.TryGetValue(key, out object? val) && keys.Count > 0)
          {
            return DrillDown(ProcessItem(val), keys);
          }
          else if (val != null && keys.Count == 0)
          {
            result.AddRange(ProcessItem(val));
          }
        }

        return result;
      }

      return null;
    }

    /// <summary>
    /// Given a Dictionary representing a thead element, return the column number of the first column that matches one of the target column names.
    /// </summary>
    /// <param name="targetColumns">A list of column names to search for.</param>
    /// <param name="thead">A dictionary representing the thead element of an XML table.</param>
    /// <returns>The column number of the first match, or -1 if no match is found.</returns>
    private static int GetTargetColNum(IList<string> targetColumns, IDictionary<string, object> thead)
    {
      var ths = DrillDown(thead, new List<string> { "tr", "th" });
      for (int i = 0; i < ths.Count(); i++)
      {
        var th = ths.TryGetAtIndex(i);
        if (th != null && th.TryGetValue("_", out object? thVal))
        {
          if (targetColumns.Contains(thVal.ToString(), StringComparer.OrdinalIgnoreCase))
          {
            return i;
          }
        }
      }

      return -1;
    }

    /// <summary>
    /// Given a Dictionary representing a table data cell, return a list of the reasons for visit. 
    /// The cell is searched for paragraphs without a styleCode="xcellHeader" attribute, content elements, or a string value.
    /// </summary>
    /// <param name="tdRaw">A dictionary representing an XML table data cell.</param>
    /// <returns>A list of the reasons for visit. If no matching elements are found, an empty list is returned.</returns>
    private static List<string> GetTextFromTd(object? tdRaw)
    {
      if (tdRaw is Dictionary<string, object> td)
      {
        // Example:
        // <td>
        //   <paragraph styleCode="xcellHeader">Diagnoses</paragraph>
        //   <paragraph>Respiratory distress</paragraph>
        // </td>
        if (td.TryGetValue("paragraph", out object? paragraphRaw))
        {
          var paragraphs = ProcessItem(paragraphRaw);
          var result = new List<string>();
          foreach (var p in paragraphs)
          {
            if (p != null && p.TryGetValue("_", out object? pVal))
            {
              p.TryGetValue("styleCode", out object? styleCode);
              if (styleCode?.ToString() != "xcellHeader")
              {
                result.Add(pVal.ToString());
              }
            }
          }

          return result;
        }

        // Example:
        // <td>
        //    <content ID="text1">Respiratory distress</content>
        // </td>
        else if (td.TryGetValue("content", out object? content))
        {
          if (content is Dictionary<string, object> contentDict && contentDict.TryGetValue("_", out object? cVal))
          {
            return new List<string>() { cVal.ToString() };
          }
        }

        // Example:
        // <td>Respiratory distress</td>
        else if (td.TryGetValue("_", out object? val))
        {
          return new List<string>() { val.ToString() };
        }
      }

      return new List<string>();
    }

    /// <summary>
    /// Given a Dictionary representing a table, return a list of the reasons for visit. The table is searched for
    /// columns named "REASON FOR VISIT", "Reason", "Diagnoses / Procedures", or "text".
    /// </summary>
    /// <param name="table">A dictionary representing an XML table.</param>
    /// <returns>A list of the reasons for visit. If no matching column is found, an empty list is returned.</returns>
    private static List<string> GetReasonsFromTable(IDictionary<string, object> table)
    {
      var targetColumns = new[] { "REASON FOR VISIT", "Reason", "Diagnoses / Procedures", "text" }.ToList();
      var result = new List<string>();
      if (table.TryGetValue("thead", out object? thead) && thead is IDictionary<string, object> theadDict)
      {
        var reasonColNum = GetTargetColNum(targetColumns, theadDict);
        var trs = DrillDown(table, new List<string> { "tbody", "tr" });

        foreach (var tr in trs)
        {
          if (tr.TryGetValue("td", out object? tdObj))
          {
            var tds = ProcessItem(tdObj);
            var td = tds.TryGetAtIndex(reasonColNum);

            result.AddRange(GetTextFromTd(td));
          }
        }
      }
      else
      {
        var trs = DrillDown(table, new List<string> { "tbody", "tr" });

        foreach (var tr in trs)
        {
          if (tr.TryGetValue("th", out object? thObj)
            && thObj is Dictionary<string, object> thDict
            && thDict.TryGetValue("_", out object? thVal)
            && targetColumns.Contains(thVal.ToString(), StringComparer.OrdinalIgnoreCase)
            && tr.TryGetValue("td", out object? td))
          {
            result.AddRange(GetTextFromTd(td));
          }
        }
      }

      return result;
    }


    /// <summary>
    /// Concatenates the reasons for visit in one or more tables into a string with ", " as the separator.
    /// </summary>
    /// <param name="data">A dictionary representing the "section" element containing the reasons for visit.</param>
    /// <returns>A concatenated string of the reasons for visit.</returns>
    public static string ConcatenateTds(IDictionary<string, object> data)
    {
      var dataDictionary = (Dictionary<string, object>)data;
      var component = dataDictionary.TryGetValue("text", out object? textComponent) ? (Dictionary<string, object>)textComponent : dataDictionary;

      if (component.TryGetValue("table", out object? table))
      {
        return string.Join(", ", GetReasonsFromTable((IDictionary<string, object>)table).Distinct(StringComparer.OrdinalIgnoreCase));
      }

      var tables = DrillDown(component, new List<string> { "list", "item", "table" });
      if (tables == null)
      {
        return "";
      }

      var result = new List<string>();
      foreach (var t in tables)
      {
        var reasons = GetReasonsFromTable(t);
        if (reasons.Count > 0)
        {
          result.AddRange(reasons);
        }
      }

      return string.Join(", ", result.Distinct(StringComparer.OrdinalIgnoreCase));
    }

    private static string WrapHtmlValue(string key, object value)
    {
      var stringBuilder = new StringBuilder();
      var tag = key;
      var addTag = supportedTags.Contains(key) || replaceTags.TryGetValue(key, out tag);
      string? tagId = null;
      IDictionary<string, object>? valueDict = value as IDictionary<string, object>;
      if (valueDict != null && valueDict.ContainsKey("ID"))
      {
        tagId = valueDict["ID"] as string;
      }

      if (addTag)
      {
        var tagHtml = tagId != null ? $"<{tag}><!-- data-id: {tagId} -->" : $"<{tag}>";
        stringBuilder.Append(tagHtml);
      }
      stringBuilder.Append(ToHtmlString(value));
      if (addTag)
      {
        stringBuilder.Append($"</{tag}>");
      }
      else
      {
        stringBuilder.Append(' ');
      }

      return stringBuilder.ToString();
    }

    private static string CleanStringFromTabs(string value)
    {
      const string reduceMultiSpace = @"[ ]{2,}";
      return Regex.Replace(value.Replace("\t", " "), reduceMultiSpace, " ");
    }

    // Overloaded method with default level value
    public static void PrintObject(object obj)
    {
      var devMode = Environment.GetEnvironmentVariable("DEV_MODE");
      var debugLog = Environment.GetEnvironmentVariable("DEBUG_LOG");
      if (devMode != "true" || debugLog != "true")
      {
        return;
      }

      PrintObject(obj, 0);
    }

    private static void PrintObject(object obj, int level)
    {
      var devMode = Environment.GetEnvironmentVariable("DEV_MODE");
      var debugLog = Environment.GetEnvironmentVariable("DEBUG_LOG");
      if (devMode != "true" || debugLog != "true")
      {
        return;
      }

      string indent = new string(' ', level * 4);

      if (obj is Dictionary<string, object> dict)
      {
        Console.WriteLine($"{indent}{{");
        foreach (var kvp in dict)
        {
          Console.Write($"{indent}    \"{kvp.Key}\": ");
          PrintObject(kvp.Value, level + 1);
        }
        Console.WriteLine($"{indent}}}");
      }
      else if (obj is List<object> list)
      {
        Console.WriteLine($"{indent}[");
        foreach (var item in list)
        {
          PrintObject(item, level + 1);
        }
        Console.WriteLine($"{indent}]");
      }
      else if (obj is string str)
      {
        Console.WriteLine($"{indent}\"{str}\",");
      }
      else
      {
        Console.WriteLine($"{indent}{obj},");
      }
    }

    /// <summary>
    /// Converts an to an HTML-formatted string.
    /// </summary>
    /// <param name="data">The data to convert, which can be of type string, IList, or IDictionary<string, object>.</param>
    /// <returns>An HTML-formatted string representing the input data.</returns>
    public static string ToHtmlString(object data)
    {
      var stringBuilder = new StringBuilder();
      if (data is string stringData)
      {
        return stringData;
      }
      else if (data is IList listData)
      {
        foreach (var row in listData)
        {
          stringBuilder.Append(ToHtmlString(row));
        }
      }
      else if (data is IDictionary<string, object> dict)
      {
        foreach (var kvp in dict)
        {
          if (kvp.Key == "_")
          {
            stringBuilder.Append(ToHtmlString(kvp.Value));
          }
          else if (kvp.Key == "br")
          {
            stringBuilder.Append("<br>");
          }
          else if (kvp.Value is IDictionary<string, object>)
          {
            stringBuilder.Append(WrapHtmlValue(kvp.Key, kvp.Value));
          }
          else if (kvp.Value is IList list)
          {
            foreach (var row in list)
            {
              stringBuilder.Append(WrapHtmlValue(kvp.Key, row));
            }
          }
        }
      }
      return CleanStringFromTabs(stringBuilder.ToString().Trim());
    }

    /// <summary>
    /// Converts an to an HTML-formatted string.
    /// </summary>
    /// <param name="data">The data to convert, which can be of type string, IList, or IDictionary<string, object>.</param>
    /// <returns>An HTML-formatted string representing the input data.</returns>
    public static string ToHtmlStringJoinBr(object data)
    {
      var stringBuilder = new StringBuilder();
      if (data is string stringData)
      {
        return stringData;
      }
      else if (data != null && data is IList listData)
      {
        for (int i = 0; i < listData.Count; i++)
        {
          stringBuilder.Append(ToHtmlStringJoinBr(listData[i]));
          if (i < listData.Count - 1)
          {
            stringBuilder.Append("<br>");
          }
        }
      }
      else if (data is IDictionary<string, object> dict)
      {
        foreach (var kvp in dict)
        {
          if (kvp.Key == "_")
          {
            stringBuilder.Append(ToHtmlStringJoinBr(kvp.Value));
          }
          else if (kvp.Key == "br")
          {
            stringBuilder.Append("<br>");
          }
          else if (kvp.Value is IDictionary<string, object>)
          {
            stringBuilder.Append(WrapHtmlValue(kvp.Key, kvp.Value));
          }
          else if (kvp.Value is IList list)
          {
            foreach (var row in list)
            {
              stringBuilder.Append(WrapHtmlValue(kvp.Key, row));
            }
          }
        }
      }
      return CleanStringFromTabs(stringBuilder.ToString().Trim());
    }

    /// <summary>
    /// Parses a CSV file containing LOINC codes and Long Common Names and returns a dictionary where the LOINC codes are keys and the LCN are values.
    /// </summary>
    /// <returns>A dictionary where the keys are LOINC codes and the values are descriptions.</returns>
    private static Dictionary<string, string> LoincDictionary()
    {
      TextFieldParser parser = new TextFieldParser("Loinc.csv");
      Dictionary<string, string> csvData = new Dictionary<string, string>();

      parser.HasFieldsEnclosedInQuotes = true;
      parser.SetDelimiters(",");

      string[]? fields;

      while (!parser.EndOfData)
      {
        fields = parser.ReadFields();
        if (fields != null)
        {
          string key = fields[0].Trim();
          string value = fields[1].Trim();
          csvData[key] = value;
        }
      }

      return csvData;
    }

    /// <summary>
    /// Retrieves the name associated with the specified LOINC code from the LOINC dictionary.
    /// </summary>
    /// <param name="loinc">The LOINC code for which to retrieve the name.</param>
    /// <returns>The name associated with the specified LOINC code, or null if the code is not found in the dictionary.</returns>
    public static string? GetLoincName(string loinc)
    {
      loincDict ??= LoincDictionary();
      loincDict.TryGetValue(loinc, out string? element);
      return element;
    }

    /// <summary>
    /// Searches for an object with a specified ID within a given data structure.
    /// </summary>
    /// <param name="data">The data structure to search within, of type IDictionary<string, object>, IList, or JArray.</param>
    /// <param name="id">The ID (reference value) to search for within the data structure.</param>
    /// <returns>An IDictionary<string, object> representing the found object with the specified ID, or null if not found.</returns>
    public static IDictionary<string, object>? FindObjectById(object data, string id)
    {
      return FindObjectByIdRecursive(data, id);
    }

    /// <summary>
    /// Recursively searches for an object with a specified ID within a given data structure.
    /// </summary>
    /// <param name="data">The data structure to search within, of type IDictionary<string, object>, IList, or JArray.</param>
    /// <param name="id">The ID to search for within the data structure.</param>
    /// <returns>An IDictionary<string, object> representing the found object with the specified ID, or null if not found.</returns>
    private static IDictionary<string, object>? FindObjectByIdRecursive(object data, string id)
    {
      if (data == null)
      {
        return null;
      }

      if (data is IDictionary<string, object> dict)
      {
        if (dict.ContainsKey("ID") && dict["ID"].ToString() == id)
        {
          return dict;
        }

        foreach (var key in dict.Keys)
        {
          var found = FindObjectByIdRecursive(dict[key], id);
          if (found != null)
          {
            return found;
          }
        }
      }

      else if (data is JArray array)
      {
        foreach (var item in array)
        {
          var found = FindObjectByIdRecursive(item, id);
          if (found != null)
          {
            return found;
          }
        }
      }
      else if (data is IList list)
      {
        foreach (var item in list)
        {
          var found = FindObjectByIdRecursive(item, id);
          if (found != null)
          {
            return found;
          }
        }
      }
      return null;
    }

    /// <summary>
    /// Concatenates strings from a given input object into a single string.
    /// </summary>
    /// <param name="input">The input data to process, which can be of type IList or IDictionary<string, object>.</param>
    /// <returns>A single concatenated string from the input data, with elements separated by spaces.</returns>
    /// <remarks> Note that if the input object is a list and all elements are strings, they appear in reverse order. This function reverses the list again so that the output string appears in the correct order.</remarks>
    public static string ConcatStrings(object input)
    {
      if (input == null) return string.Empty;

      if (input is IList list)
      {
        // If all elements are strings, reverse the list
        bool allElementsAreStrings = list.Cast<object>().All(row => row is string);
        if (allElementsAreStrings)
        {
          return string.Join("<br/>", list.Cast<object>().Reverse().ToList());
        }
        else
        {
          List<string> result = new List<string>();

          foreach (var item in list)
          {
            if (item is null)
            {
              continue;
            }
            else if (item is IDictionary<string, object> dict)
            {
              foreach (var kvp in dict)
              {
                result.Add(kvp.Value?.ToString() ?? "");
              }
            }
            else
            {
              result.Add(item.ToString() ?? "");
            }
          }
          return string.Join("<br/>", result);
        }
      }
      else if (input is IDictionary<string, object> dictObject)
      {
        List<string> result = new List<string>();

        foreach (var kvp in dictObject)
        {
          if (kvp.Key == "styleCode")
          {
            continue;
          }
          if (kvp.Value is IDictionary<string, object> nestedDict)
          {
            result.Add(ConcatStrings(nestedDict));
          }
          else if (kvp.Value is IList nestedList)
          {
            List<string> nestedValues = new List<string>();
            for (int i = nestedList.Count - 1; i >= 0; i--)
            {
              var item = nestedList[i];
              if (item is IDictionary<string, object> nestedDictInList)
              {
                nestedValues.Add(ConcatStrings(nestedDictInList));
              }
              else if (item is string listItemString)
              {
                nestedValues.Add(listItemString);
              }
            }
            result.Add(string.Join("<br/>", nestedValues));
          }
          else
          {
            result.Add(kvp.Value?.ToString() ?? "");
          }
        }
        return string.Join("<br/>", result);
      }
      return string.Empty;
    }

    /// <summary>
    /// Formats quantity into valid json number.
    /// </summary>
    /// <param name="input">The input data to process, which is a number formatted as a string.</param>
    /// <returns>A number formatted as a string, with a leading 0 if it's a decimal, and up to 3 decimal places.</returns>
    public static string FormatQuantity(string input)
    {
      IConvertible convert = input;
      return convert.ToDouble(null).ToString("0.###");
    }
  }
}