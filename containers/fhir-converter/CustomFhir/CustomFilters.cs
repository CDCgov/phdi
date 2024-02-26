using System;
using System.Collections.Generic;
using System.Collections;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Newtonsoft.Json;

namespace Microsoft.Health.Fhir.Liquid.Converter
{
  /// <summary>
  /// Filters for conversion
  /// </summary>
  public partial class Filters
  {
    private static HashSet<string> supportedTags = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "br", "li", "ol", "p", "span", "table", "tbody", "td", "textarea", "th", "thead", "tr", "u", "ul" };
    private static Dictionary<string, string> replaceTags = new Dictionary<string, string>{
        {"list", "ul"},
        {"item", "li"}
    };

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
      if (addTag)
      {
        stringBuilder.Append($"<{tag}>");
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
  }
}
