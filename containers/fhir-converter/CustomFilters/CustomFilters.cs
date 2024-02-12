using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Health.Fhir.Liquid.Converter.InputProcessors;
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
       if(data is string)
       {
           return data as string;
       }
       else if(data is IList<object>)
       {
        foreach(var row in data as IList<object>)
        {
          stringBuilder.Append(ToHtmlString(row));
        }
       }
       else if(data is IDictionary<string, object>)
       {
           var dict = data as IDictionary<string, object>;
           foreach(var item in dict)
           {
               if(item.Key == "_")
               {
                  stringBuilder.Append(ToHtmlString(item.Value));
               }
               else if(item.Key == "br")
               {
                   stringBuilder.Append("<br>");
               }
               else if (item.Value is IDictionary<string, object>)
               {
                   var addTag = supportedTags.Contains(item.Key);
                   if(addTag)
                   {
                       stringBuilder.Append($"<{item.Key}>");
                   }
                   stringBuilder.Append(ToHtmlString(item.Value));
                   if(addTag)
                   {
                       stringBuilder.Append($"</{item.Key}>");
                   }
               }
               else if(item.Value is IList<object>)
               {
                  foreach(var row in item.Value as IList<object>)
                  {
                    var addTag = supportedTags.Contains(item.Key);
                    if(addTag)
                    {
                        stringBuilder.Append($"<{item.Key}>");
                    }
                    stringBuilder.Append(ToHtmlString(row));
                    if(addTag)
                    {
                        stringBuilder.Append($"</{item.Key}>");
                    }
                  }
               }
           }
       }
       return stringBuilder.ToString();
    }
  }
}

