import { Icon } from "@trussworks/react-uswds";
import { DefinedValueSetCollection } from "../CustomizeQuery";
import customAccordionStyles from "./customizeQueryAccordion.module.css";

type CustomizeQueryAccordionBodyProps = {
  group: DefinedValueSetCollection;
  toggleInclude: (groupIndex: number, itemIndex: number) => void;
  groupIndex: number;
};

const CustomizeQueryAccordionBody: React.FC<
  CustomizeQueryAccordionBodyProps
> = ({ group, toggleInclude, groupIndex }) => {
  console.log("in child body component", group.items);
  return (
    <div className="padding-bottom-3">
      <div className="customize-query-grid-container customize-query-table">
        <div className="customize-query-grid-header margin-top-10">
          <div className="accordion-table-header">Include</div>
          <div className="accordion-table-header">Code</div>
          <div className="accordion-table-header">Display</div>
        </div>
        <div className="customize-query-grid-body">
          {group.items.map((item, index) => (
            <div
              className="customize-query-grid-row customize-query-striped-row"
              key={item.code}
            >
              <div
                className={`hide-checkbox-label margin-4 ${customAccordionStyles.checkboxLabel} `}
                onClick={(e) => {
                  e.stopPropagation();
                  toggleInclude(groupIndex, index);
                }}
              >
                {item.include && (
                  <Icon.Check
                    className="usa-icon"
                    style={{ backgroundColor: "white" }}
                    size={4}
                    color="#005EA2"
                  />
                )}
              </div>
              <div>{item.code}</div>
              <div>{item.display}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CustomizeQueryAccordionBody;
