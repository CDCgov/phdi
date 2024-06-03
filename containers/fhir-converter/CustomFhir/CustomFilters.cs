using System;
using System.Collections.Generic;
using System.Collections;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Microsoft.VisualBasic.FileIO;

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
        {"item", "li"}
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

    private static Dictionary<string, object>? DrillDown(Dictionary<string, object> item, List<string> list)
    {
      if (list.Count == 0)
      {
        return item;
      }
      string firstElement = list.First(); // Retrieve the first element
      list.Remove(firstElement);
      if (item.TryGetValue(firstElement, out object? element) && list.Count > 0)
      {
        return DrillDown((Dictionary<string, object>)element, list);
      }
      else if (element != null && list.Count == 0)
      {
        return element as Dictionary<string, object>;
      }
      else
      {
        return null;
      }
    }
    public static string ConcatenateTds(IDictionary<string, object> data)
    {
      var result = new List<string>();
      var dataDictionary = (Dictionary<string, object>)data;
      var component = DrillDown(dataDictionary, new List<string> { "text" }) ??
        dataDictionary;
      var tbody = DrillDown(component, new List<string> { "list", "item", "table", "tbody" }) ??
        DrillDown(component, new List<string> { "table", "tbody" });

      if (tbody != null && tbody.TryGetValue("tr", out object? tr))
      {
        var trs = ProcessItem(tr);
        if (trs != null && trs.Count != 0)
        {
          foreach (var r in trs)
          {
            if (r.TryGetValue("td", out object? rawTds))
            {
              var tds = ProcessItem(rawTds);
              if (tds != null && tds.Count != 0)
              {
                foreach (var d in tds)
                {
                  if (d != null && d.TryGetValue("_", out object? val))
                  {
                    result.Add((string)val);
                  }
                }
              }
            }
          }
        }
      }
      return string.Join(",", result);
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
        var tagHtml = tagId != null ? $"<{tag} data-id='{tagId}'>" : $"<{tag}>";
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

    private static void PrintObject(object obj, int level)
    {
      string indent = new string(' ', level * 4);

      if (obj is Dictionary<string, object> dict)
      {
        foreach (var kvp in dict)
        {
          Console.WriteLine($"{indent}{kvp.Key}:");
          PrintObject(kvp.Value, level + 1);
        }
      }
      else if (obj is List<object> list)
      {
        foreach (var item in list)
        {
          Console.Write($"{indent}- ");
          PrintObject(item, level + 1);
        }
      }
      else
      {
        Console.WriteLine($"{indent}{obj}");
      }
    }

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
          // TODO: DELETE
          // Console.WriteLine($"Key: {kvp.Key}, Value: {kvp.Value}");
          if (kvp.Key == "br")
          {
            stringBuilder.Append("<br>");
          }
          else if (kvp.Value is IList list)
          {
            // For Lists where all elements are strings, (i.e., content with <br>), they are showing up in reverse order
            bool allElementsAreStrings = list.Cast<object>().All(row => row is string);
            if (allElementsAreStrings)
            {
              Console.WriteLine("All Elements are Strings!");
              list = list.Cast<object>().Reverse().ToList();
            }
            foreach (var row in list)
            {
              if (row is string)
              {
              // Console.WriteLine($"LIST IS STRING! data: {list}, Row: {row}");
              // PrintObject(list.Cast<object>().ToList(), 0);
              }
              stringBuilder.Append(WrapHtmlValue(kvp.Key, row));
            }
          }
          else if (kvp.Key == "_")
          {
            stringBuilder.Append(ToHtmlString(kvp.Value));
          }
          else if (kvp.Value is IDictionary<string, object>)
          {
            stringBuilder.Append(WrapHtmlValue(kvp.Key, kvp.Value));
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
    
    // TODO: Add Docs
    // TODO: Remove logs
    public static IDictionary<string, object>  FindObjectById(object data, string id)
    {
      // Console.WriteLine($"------ SEARCHING FOR ID: {id}");
      return FindObjectByIdRecursive(data, id);
    }

    // TODO: Add Docs
    // TODO: Remove logs
    private static IDictionary<string, object>  FindObjectByIdRecursive(object data, string id)
    {
      // Console.WriteLine("FindObjectByIdRecursive function running");
      if (data == null)
      {
        // Console.WriteLine("FindObjectByIdRecursive token is null");
        return null;
      }

      if (data is IDictionary<string, object> dict)
      {
        // Console.WriteLine($"Checking object: {dict}");
        if (dict.ContainsKey("ID") && dict["ID"].ToString() == id)
        {
          // Console.WriteLine($"Found object with ID: {id}");
          return dict;
        }

        foreach (var key in dict.Keys)
        {
          // Console.WriteLine($"Checking key: {key}, {dict[key]}");
          var found = FindObjectByIdRecursive(dict[key], id);
          if (found != null)
          {
            return found;
          }
        }
      }

      else if (data is JArray array)
      {
        // Console.WriteLine($"data is an array: {array}");
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
        // Console.WriteLine($"data is a list: {list}");
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

    // TODO: Add Docs
    // TODO: Remove logs
    public static string ConcatStrings(object input)
    {
      // Console.WriteLine($"---------- INPUT: {input}");
      if (input == null) return string.Empty;

      if (input is IList list)
      {
        // If all elements are strings, reverse the list
        bool allElementsAreStrings = list.Cast<object>().All(row => row is string);
        if (allElementsAreStrings)
        {
          // Console.WriteLine($"Array, and all elements are strings");
          return string.Join(" ", list.Cast<object>().Reverse().ToList());
        }
        else
        {
          List<string> result = new List<string>();

          foreach (var item in list)
          {
            // Console.WriteLine($"List, and all elements are objects");
            if (item is IDictionary<string, object> dict)
            {
              // Console.WriteLine($"List, and all elements are dictionaries");
              foreach (var kvp in dict)
              {
                result.Add(kvp.Value.ToString());
              }
            }
            else
            {
              result.Add(item.ToString());
            }
          }
          // Console.WriteLine($"RESULT: {string.Join(" ", result)}");
          return string.Join(" ", result); 
        }
      }

      else if (input is IDictionary<string, object> dictObject)
      {
        List<string> result = new List<string>();
        foreach (var kvp in dictObject)
          {
            result.Add(kvp.Value.ToString());
          }
        return string.Join(" ", result);
      }
      // Console.WriteLine("Returning an empty string");
      return string.Empty;
    }
  }
}
