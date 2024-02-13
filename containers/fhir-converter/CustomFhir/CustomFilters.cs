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
    private static HashSet<string> supportedTags = new HashSet<string>(StringComparer.OrdinalIgnoreCase){"b", "br", "li", "ol", "p", "span", "table", "tbody", "td", "textarea", "th", "thead", "tr", "u", "ul"};

    // Items from the filter could be arrays or objects, process them to be the same
    private static List<Dictionary<string, object>> ProcessItem(object item)
    {
        if (item is Dictionary<string, object> dict)
        {
            return new List<Dictionary<string, object>> { dict };
        }
        else if (item is IEnumerable<object> collection)
        {
            return collection.Select(x => x as Dictionary<string, object>).ToList();
        }
        else if (item is IEnumerable<Dictionary<string, object>> collectionTwo)
        {
            return collectionTwo.Select(x => x as Dictionary<string, object>).ToList();
        }
        return new List<Dictionary<string, object>>();
    }

    private static Dictionary<string, object> DrillDown(Dictionary<string, object> item, List<string> list){
      if(list.Count == 0){
        return item;
      }
      string firstElement = list.First(); // Retrieve the first element
      list.Remove(firstElement);
      var element = item.GetValueOrDefault(firstElement, null);
      if(element != null && list.Count > 0){
        return DrillDown(element as Dictionary<string, object>, list);
      }else if(element !=null && list.Count == 0){
        return element as Dictionary<string, object>;
      }else{
        return null;
      }
    }
    public static string ConcatenateTds(IDictionary<string, object> data)
    {
      var result = new List<string>();
      var dataDictionary = (data as Dictionary<string, object>);
      var component = DrillDown(dataDictionary, new List<string> {"text"}) ??
        dataDictionary;
      var tbody = DrillDown(component, new List<string> {"list", "item", "table", "tbody"}) ??
        DrillDown(component, new List<string> {"table", "tbody"});
      
      var tr = tbody?.GetValueOrDefault("tr");
      var trs = ProcessItem(tr);

      if(trs != null && trs.Count != 0){
        foreach (var r in trs){
          var rawTds = r.GetValueOrDefault("td");
          var tds = ProcessItem(rawTds);
          if(tds != null && tds.Count != 0){
            foreach(var d in tds){
              if(d != null && d.GetValueOrDefault("_", null) != null){
                  result.Add(d.GetValueOrDefault("_") as string);
              }
            }
          }
        }
      }
      return string.Join(",", result);
    }

    public static string ToHtmlString(object data)
    {
       var stringBuilder = new StringBuilder();
       if(data is string stringData)
       {
           return stringData;
       }
       else if(data is IList listData)
       {
        foreach(var row in listData)
        {
          stringBuilder.Append(ToHtmlString(row));
        }
       }
       else if(data is IDictionary<string, object> dict)
       {
           foreach(var kvp in dict)
           {
               if(kvp.Key == "_")
               {
                  stringBuilder.Append(ToHtmlString(kvp.Value));
               }
               else if(kvp.Key == "br")
               {
                   stringBuilder.Append("<br>");
               }
               else if (kvp.Value is IDictionary<string, object>)
               {
                   var addTag = supportedTags.Contains(kvp.Key);
                   if(addTag)
                   {
                       stringBuilder.Append($"<{kvp.Key}>");
                   }
                   stringBuilder.Append(ToHtmlString(kvp.Value));
                   if(addTag)
                   {
                       stringBuilder.Append($"</{kvp.Key}>");
                   }
               }
               else if(kvp.Value is IList listKvp)
               {
                  foreach(var row in listKvp)
                  {
                    var addTag = supportedTags.Contains(kvp.Key);
                    if(addTag)
                    {
                        stringBuilder.Append($"<{kvp.Key}>");
                    }
                    stringBuilder.Append(ToHtmlString(row));
                    if(addTag)
                    {
                        stringBuilder.Append($"</{kvp.Key}>");
                    }
                  }
               }
           }
       }
       return stringBuilder.ToString();
    }
  }
}

