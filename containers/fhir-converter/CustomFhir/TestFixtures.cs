using System.Collections;

namespace CustomFhir;

public class CustomFilterTestFixtures : IEnumerable<object[]>
{
  public IEnumerator<object[]> GetEnumerator()
  {
    yield return new object[] { ReasonsForVisitKY, "Reason 1" };
    yield return new object[] { ReasonsForVisitLA, "Reason 1" };
    yield return new object[] { ReasonsForVisitTN, "Reason 1, Reason 2" };
  }

  IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

  // <text>
  //   <list>
  //     <item>
  //       <table>
  //         <colgroup>
  //           <col />
  //           <col />
  //         </colgroup>
  //         <thead>
  //           <tr>
  //             <th>Reason</th>
  //             <th>Comments</th>
  //           </tr>
  //         </thead>
  //         <tbody>
  //           <tr>
  //             <td>Reason 1</td>
  //             <td>Some notes</td>
  //           </tr>
  //         </tbody>
  //       </table>
  //     </item>
  //   </list>
  // </text>
  private Dictionary<string, object> ReasonsForVisitKY = new Dictionary<string, object> {
    { "text", new Dictionary<string, object> {
      { "list", new List<Dictionary<string, object>>() {
        new Dictionary<string, object>() {
          { "item", new Dictionary<string, object>() {
              { "table", new List<Dictionary<string, object>>() {
                  new Dictionary<string, object>() {
                    { "colgroup", new Dictionary<string, object>() {
                      { "col", new List<Dictionary<string, object>>() {
                        null!,
                        null!,
                      }}
                    }},
                    { "thead", new Dictionary<string, object>() {
                      { "tr", new Dictionary<string, object>(){
                        { "th", new List<object> {
                          new Dictionary<string, object> {{ "_", "Reason" }},
                      new Dictionary<string, object> {{ "_", "Comments" }}
                        }}
                      }}
                    } },
                    { "tbody", new Dictionary<string, object>() {
                      { "tr", new Dictionary<string, object>(){
                        { "td", new List<Dictionary<string, object>?> {
                          new Dictionary<string, object> {{ "_", "Reason 1" }},
                          new Dictionary<string, object> {{ "_", "Some notes" }}
                        }}
                      }}
                    }}
                  }
              }}
          }}
        }
      }}
    }}
  };

  // <text>
  //   <table>
  //     <tbody>
  //       <tr>
  //         <th>Reason for Visit</th>
  //         <td>TESTING FOR ECR</td>
  //       </tr>
  //     </tbody>
  //   </table>
  // </text>
  private Dictionary<string, object> ReasonsForVisitLA = new Dictionary<string, object> {
    { "title", new Dictionary<string, object> {{ "_", "Reason for Visit" }} },
    { "text", new Dictionary<string, object> {
      { "table", new Dictionary<string, object> {
        { "tbody", new Dictionary<string, object>() {
          { "tr", new Dictionary<string, object>() {
            { "th", new Dictionary<string, object> {{ "_", "Reason for Visit" } }},
            { "td", new Dictionary<string, object> {{ "_", "Reason 1" } }}
          }}
        }}
      }}
    }}
  };

  // <title>Reason for Visit</title>
  // <text>
  //     <list>
  //       <item>
  //         <table>
  //           <colgroup>
  //             <col />
  //             <col />
  //           </colgroup>
  //           <thead>
  //             <tr>
  //               <th>Reason</th>
  //               <th>Comments</th>
  //             </tr>
  //           </thead>
  //           <tbody>
  //             <tr>
  //               <td>Reason 1</td>
  //               <td />
  //             </tr>
  //           </tbody>
  //         </table>
  //       </item>
  //       <item>
  //         <caption>Auth/Cert (Routine)</caption>
  //         <table>
  //           <colgroup>
  //             <col />
  //           </colgroup>
  //           <thead>
  //             <tr>
  //               <th>Specialty</th>
  //               <th>Diagnoses / Procedures</th>
  //               <th>Referred By Contact</th>
  //               <th>Referred To Contact</th>
  //             </tr>
  //           </thead>
  //           <tbody>
  //             <tr>
  //               <td />
  //               <td>
  //                 <paragraph styleCode="xcellHeader">Diagnoses</paragraph>
  //                 <paragraph>Reason 2</paragraph>
  //                 <paragraph />
  //                 <br />
  //               </td>
  //               <td>
  //                 <paragraph />
  //               </td>
  //               <td>
  //                 <paragraph />
  //               </td>
  //             </tr>
  //           </tbody>
  //         </table>
  //         <table>
  //           <colgroup>
  //             <col />
  //             <col />
  //             <col />
  //             <col />
  //             <col />
  //             <col />
  //             <col />
  //           </colgroup>
  //           <thead>
  //             <tr>
  //               <th>Referral ID</th>
  //               <th>Status</th>
  //               <th>Reason</th>
  //               <th>Start Date</th>
  //               <th>Expiration Date</th>
  //               <th>Visits Requested</th>
  //               <th>Visits Authorized</th>
  //             </tr>
  //           </thead>
  //           <tbody>
  //             <tr>
  //               <td>19268797</td>
  //               <td styleCode="xflagData" />
  //               <td />
  //               <td />
  //               <td />
  //               <td>1</td>
  //               <td>1</td>
  //             </tr>
  //           </tbody>
  //         </table>
  //         <br />
  //       </item>
  //     </list>
  //  </text>
  private Dictionary<string, object> ReasonsForVisitTN = new Dictionary<string, object> {
    {
    "title", new Dictionary<string, object> {{ "_", "Reason for Visit" }}
    },
    { "text", new Dictionary<string, object> {
      { "list", new List<Dictionary<string, object>>() {
        new Dictionary<string, object>() {
          { "item", new List<Dictionary<string, object>>() {
            new Dictionary<string, object>() {
              { "table", new List<Dictionary<string, object>>() {
                  new Dictionary<string, object>() {
                    { "colgroup", new Dictionary<string, object>() {
                      { "col", new List<Dictionary<string, object>>() {
                        null!,
                        null!,
                      }}
                    }},
                    { "thead", new Dictionary<string, object>() {
                      { "tr", new Dictionary<string, object>(){
                        { "th", new List<object> {
                          new Dictionary<string, object> {{ "_", "Reason" }},
                      new Dictionary<string, object> {{ "_", "Comments" }}
                        }}
                      }}
                    } },
                    { "tbody", new Dictionary<string, object>() {
                      { "tr", new Dictionary<string, object>(){
                        { "td", new List<Dictionary<string, object>?> {
                          new Dictionary<string, object> {{ "_", "Reason 1" }},
                          null
                        }}
                      }}
                    }}
                  }
              }}
            },
            new Dictionary<string, object> {
              { "caption", new Dictionary<string, object> {{ "_", "Auth/Cert (Routine)" }} },
              { "table", new Dictionary<string, object>() {
                { "colgroup", new Dictionary<string, object?>()
                  {{ "col", null }}
                },
                { "thead", new Dictionary<string, object>() {
                  { "tr", new Dictionary<string, object>(){
                    { "th", new List<object> {
                      new Dictionary<string, object> {{ "_", "Specialty" }},
                      new Dictionary<string, object> {{ "_", "Diagnoses / Procedures" }},
                      new Dictionary<string, object> {{ "_", "Referred to By Contact" }},
                      new Dictionary<string, object> {{ "_", "Referred to Contact" }}
                    }}
                  }}
                } },
                { "tbody", new Dictionary<string, object>() {
                  { "tr", new Dictionary<string, object>(){
                    { "td", new List<Dictionary<string, object>?> {
                      null,
                      new Dictionary<string, object> {
                        { "paragraph", new List<Dictionary<string, object>?>() {
                          new Dictionary<string, object> {
                            { "styleCode", "xcellHeader" }, { "_", "Diagnoses" }
                          },
                          new Dictionary<string, object> {
                            { "_", "Reason 2" }
                          },
                          null
                        }},
                        { "br", null! }
                      },
                      new Dictionary<string, object> {
                        { "paragraph", new List<Dictionary<string, object>?>() {
                          null
                        }}
                      },
                      new Dictionary<string, object> {
                        { "paragraph", new List<Dictionary<string, object>?>() {
                          null
                        }}
                      }
                    }}
                  }}
                }}
              }}
            },
            new Dictionary<string, object>() {
              { "table", new Dictionary<string, object>() {
                { "colgroup", new Dictionary<string, object>()
                  {{ "col", new List<Dictionary<string, object>>() {
                    null!,
                    null!,
                    null!,
                    null!,
                    null!,
                    null!,
                    null!
                  } }}
                },
                { "thead", new Dictionary<string, object>() {
                  { "tr", new Dictionary<string, object>(){
                    { "th", new List<object> {
                      new Dictionary<string, object> {{ "_", "Referral" }},
                      new Dictionary<string, object> {{ "_", "Status" }},
                      new Dictionary<string, object> {{ "_", "Reason" }},
                      new Dictionary<string, object> {{ "_", "Start Date" }},
                      new Dictionary<string, object> {{ "_", "Expiration Date" }},
                      new Dictionary<string, object> {{ "_", "Visits Requested" }},
                      new Dictionary<string, object> {{ "_", "Visits Authorized" }}
                    }}
                  }}
                }},
                { "tbody", new Dictionary<string, object>() {
                  { "tr", new Dictionary<string, object>(){
                    { "td", new List<object?> {
                      new Dictionary<string, object> {{ "_", "1234567" }},
                      new Dictionary<string, object> {{ "styleCode", "xflagData" }},
                      null,
                      null,
                      null,
                      new Dictionary<string, object> {{ "_", "1" }},
                      new Dictionary<string, object> {{ "_", "1" }}
                    }}
                  }}
                }}
              }}
            }

          }}
        }
      }}
    }}
  };
}