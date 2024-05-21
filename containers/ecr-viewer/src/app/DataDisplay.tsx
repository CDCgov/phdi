import React, { ReactNode, useEffect, useState } from "react";
import { Button } from "@trussworks/react-uswds";
import classNames from "classnames";
import { ToolTipElement } from "@/app/ToolTipElement";

export interface DisplayDataProps {
  title?: string;
  className?: string;
  toolTip?: string;
  value?: string | React.JSX.Element | React.JSX.Element[] | React.ReactNode;
  dividerLine?: boolean;
}

/**
 * Functional component for displaying data.
 * @param props - Props for the component.
 * @param props.item - The display data item to be rendered.
 * @param [props.className] - Additional class name for styling purposes.
 * @returns - A React element representing the display of data.
 */
export const DataDisplay: React.FC<{
  item: DisplayDataProps;
  className?: string;
}> = ({
  item,
  className,
}: {
  item: DisplayDataProps;
  className?: string;
}): React.JSX.Element => {
  item.dividerLine =
    item.dividerLine == null || item.dividerLine == undefined
      ? true
      : item.dividerLine;
  return (
    <div>
      <div className="grid-row">
        <div className="data-title">
          <ToolTipElement content={item.title} toolTip={item.toolTip} />
        </div>
        <div
          className={classNames(
            "grid-col-auto maxw7 text-pre-line",
            className,
            item.className ? item.className : "",
          )}
        >
          <FieldValue>{item.value}</FieldValue>
        </div>
      </div>
      {item.dividerLine ? <div className={"section__line_gray"} /> : ""}
    </div>
  );
};
/**
 * Functional component for displaying a value. If the value has a length greater than 500 characters, it will be split after 300 characters with a view more button to view the entire value.
 * @param value - props for the component
 * @param value.children - the value to be displayed in the value
 * @returns - A React element representing the display of the value
 */
const FieldValue: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const maxLength = 500;
  const cutLength = 300;
  const [hidden, setHidden] = useState(true);
  const [fieldValue, setFieldValue] = useState(children);
  const valueLength = getReactNodeLength(children);
  const cutField = trimField(children, cutLength, setHidden).value;
  useEffect(() => {
    if (valueLength > maxLength) {
      if (hidden) {
        setFieldValue(cutField);
      } else {
        setFieldValue(
          <>
            {children}&nbsp;
            <Button
              type={"button"}
              unstyled={true}
              onClick={() => setHidden(true)}
            >
              View less
            </Button>
          </>,
        );
      }
    }
  }, [hidden]);

  return fieldValue;
};
/**
 * Recursively determine the character length of a ReactNode
 * @param value - react node to be measured
 * @returns - the number of characters in the ReactNode
 */
const getReactNodeLength = (value: React.ReactNode): number => {
  if (typeof value === "string") {
    return value.length;
  } else if (Array.isArray(value)) {
    let count = 0;
    value.forEach((val) => (count += getReactNodeLength(val)));
    return count;
  } else if (React.isValidElement(value) && value.props.children) {
    return getReactNodeLength(value.props.children);
  }
  return 0;
};
/**
 * Create an element with `remainingLength` length followed by a view more button
 * @param value - the value that will be cut
 * @param remainingLength - the length of how long the returned element will be
 * @param setHidden - a function used to signify that the view more button has been clicked.
 * @returns - an object with the shortened value and the length left over.
 */
const trimField = (
  value: React.ReactNode,
  remainingLength: number,
  setHidden: (val: boolean) => void,
): { value: React.ReactNode; remainingLength: number } => {
  if (remainingLength < 1) {
    return { value: null, remainingLength };
  }
  if (typeof value === "string") {
    const cutString = value.substring(0, remainingLength);
    if (remainingLength - cutString.length === 0) {
      return {
        value: (
          <>
            {cutString}...&nbsp;
            <Button
              type={"button"}
              unstyled={true}
              onClick={() => setHidden(false)}
            >
              View more
            </Button>
          </>
        ),
        remainingLength: 0,
      };
    }
    return {
      value: cutString,
      remainingLength: remainingLength - cutString.length,
    };
  } else if (Array.isArray(value)) {
    let newValArr = [];
    for (let i = 0; i < value.length; i++) {
      let splitVal = trimField(value[i], remainingLength, setHidden);
      remainingLength = splitVal.remainingLength;
      newValArr.push(
        <React.Fragment key={`arr-${i}-${splitVal.value}`}>
          {splitVal.value}
        </React.Fragment>,
      );
    }
    return { value: newValArr, remainingLength: remainingLength };
  } else if (React.isValidElement(value) && value.props.children) {
    let childrenCopy: ReactNode;
    if (Array.isArray(value.props.children)) {
      childrenCopy = [...value.props.children];
    } else {
      childrenCopy = value.props.children;
    }
    let split = trimField(childrenCopy, remainingLength, setHidden);
    const newElement = React.cloneElement(
      value,
      { ...value.props },
      split.value,
    );
    return { value: newElement, remainingLength: split.remainingLength };
  }
  return { value, remainingLength: remainingLength };
};
