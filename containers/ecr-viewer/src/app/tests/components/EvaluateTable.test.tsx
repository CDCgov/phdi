import { loadYamlConfig } from "@/app/api/utils";
import { render, screen } from "@testing-library/react";
import { PathMappings } from "@/app/utils";
import userEvent from "@testing-library/user-event";
import EvaluateTable, {
  BuildHeaders,
  BuildTable,
  ColumnInfoInput,
} from "@/app/view-data/components/EvaluateTable";
import { JSX } from "react";

const mappings = loadYamlConfig();

describe("Evaluate table", () => {
  it("should create an empty table with a caption", () => {
    render(
      <EvaluateTable
        resources={[]}
        mappings={mappings}
        columns={[]}
        caption={"Table Caption"}
      />,
    );

    expect(screen.getByText("Table Caption")).toBeInTheDocument();
    expect(screen.getByTestId("table")).toBeInTheDocument();
  });
  it("should create a table with 1 row using the provided value", () => {
    render(
      <EvaluateTable
        resources={[{}]}
        mappings={mappings}
        columns={[{ columnName: "Col1", value: "Data1" }]}
      />,
    );

    expect(screen.getByText("Col1")).toBeInTheDocument();
    expect(screen.getByText("Data1")).toBeInTheDocument();
  });
  it("should create a table with 1 row evaluate the fhir element", () => {
    render(
      <EvaluateTable
        resources={[{ id: "id1" }]}
        mappings={{ id: "id" }}
        columns={[{ columnName: "Col1", infoPath: "id" }]}
      />,
    );

    expect(screen.getByText("Col1")).toBeInTheDocument();
    expect(screen.getByText("id1")).toBeInTheDocument();
  });
  it("should create a table and apply a function to the row value", () => {
    render(
      <EvaluateTable
        resources={[{ id: "id1" }]}
        mappings={{ getId: "id" }}
        columns={[
          {
            columnName: "Col1",
            infoPath: "getId",
            applyToValue: (value) => value?.toUpperCase(),
          },
        ]}
      />,
    );

    expect(screen.getByText("Col1")).toBeInTheDocument();
    expect(screen.getByText("ID1")).toBeInTheDocument();
  });
  it("should not apply a function to the row value if value is null", () => {
    render(
      <EvaluateTable
        resources={[{}]}
        mappings={{ getId: "id" }}
        columns={[
          {
            columnName: "Col1",
            infoPath: "getId",
            applyToValue: (value) => value?.toUpperCase(),
          },
        ]}
      />,
    );

    expect(screen.getByText("Col1")).toBeInTheDocument();
    expect(screen.getByText("No data")).toBeInTheDocument();
  });
  describe("hiddenBaseText", () => {
    const pathMapping: PathMappings = { idPath: "id", notePath: "note.text" };
    describe("single column", () => {
      const columnInfo: ColumnInfoInput[] = [
        {
          infoPath: "notePath",
          columnName: "Lab notes",
          hiddenBaseText: "notes",
        },
      ];

      it("should show view notes button", () => {
        const fhirResource = [
          {
            note: [
              {
                text: "wow this is interesting",
              },
            ],
          } as any,
        ];
        render(
          <EvaluateTable
            resources={fhirResource}
            mappings={pathMapping}
            columns={columnInfo}
          />,
        );

        expect(screen.getByText("View notes")).toBeInTheDocument();
        expect(screen.queryByText("wow this is interesting")).not.toBeVisible();
      });
      it("should show notes text and replace 'View notes' with 'Hide notes' when 'View notes' button is clicked", async () => {
        const user = userEvent.setup();
        const pathMapping: PathMappings = { notePath: "note.text" };
        const fhirResource = [
          {
            note: [
              {
                text: "wow this is interesting",
              },
            ],
          } as any,
        ];
        render(
          <EvaluateTable
            resources={fhirResource}
            mappings={pathMapping}
            columns={columnInfo}
          />,
        );

        await user.click(screen.getByText("View notes"));

        expect(screen.queryByText("View notes")).not.toBeInTheDocument();
        expect(screen.getByText("Hide notes")).toBeInTheDocument();
        expect(screen.getByText("wow this is interesting")).toBeVisible();
      });
      it("should only open one note when 'View notes' is clicked", async () => {
        const user = userEvent.setup();
        const fhirResource = [
          {
            note: [
              {
                text: "wow this is interesting",
              },
            ],
          } as any,
          {
            note: [
              {
                text: "no one should see this",
              },
            ],
          },
        ];

        render(
          <EvaluateTable
            resources={fhirResource}
            mappings={pathMapping}
            columns={columnInfo}
          />,
        );

        await user.click(screen.getAllByText("View notes")[0]);

        expect(screen.getAllByText("View notes")).toHaveLength(1);
        expect(screen.getByText("no one should see this")).not.toBeVisible();
      });
    });
    it("should span across the whole table", async () => {
      const columnInfo: ColumnInfoInput[] = [
        {
          columnName: "id",
          infoPath: "idPath",
        },
        {
          columnName: "Lab notes",
          infoPath: "notePath",
          hiddenBaseText: "notes",
        },
      ];
      const fhirResource = [
        {
          id: "1234",
          note: [
            {
              text: "wow this is interesting",
            },
          ],
        } as any,
      ];

      render(
        <EvaluateTable
          resources={fhirResource}
          mappings={pathMapping}
          columns={columnInfo}
        />,
      );

      expect(screen.getByText("wow this is interesting")).toHaveAttribute(
        "colSpan",
        "2",
      );
    });
  });
});

describe("BuildHeaders", () => {
  it("should render headers with correct names and class names", () => {
    const columns = [
      { columnName: "Column 1", className: "custom-class-1" },
      { columnName: "Column 2", className: "custom-class-2" },
    ];

    const headers = BuildHeaders(columns);

    headers.forEach((header, index) => {
      expect(header.props.children).toEqual(columns[index].columnName);
      expect(header.props.className).toContain(columns[index].className);
    });
  });
});

describe("BuildTable", () => {
  let headers: JSX.Element[], tableRows: JSX.Element[];

  beforeEach(() => {
    headers = [
      <th key="column1" className="tableHeader">
        Column 1
      </th>,
      <th key="column2" className="tableHeader">
        Column 2
      </th>,
    ];

    tableRows = [
      <tr key="row1">
        <td>Row 1, Col 1</td>
        <td>Row 1, Col 2</td>
      </tr>,
    ];
  });

  it("should render table with correct class name", () => {
    const { container } = render(
      <BuildTable
        headers={headers}
        tableRows={tableRows}
        caption="Table Test"
        className="custom-class-1 custom-class-2"
      />,
    );
    const tableElement = container.querySelector("table");

    expect(tableElement).toHaveClass("custom-class-1");
    expect(tableElement).toHaveClass("custom-class-2");
  });
});
