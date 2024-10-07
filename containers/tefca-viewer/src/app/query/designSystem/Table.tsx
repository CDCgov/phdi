import { Table as TrussTable } from "@trussworks/react-uswds";

type TableProps = {
  children: React.ReactNode;
  className?: string;
  bordered?: boolean;
  striped?: boolean;
};

/**
 *
 * @param root0 - params
 * @param root0.children - the child table component to render
 * @param root0.bordered - whether to render a bordered table
 * @param root0.striped - whether to render a striped table
 * @param root0.className - additional custom class names
 * @returns - A UWSDS-styled table
 */
const Table: React.FC<TableProps> = ({
  children,
  bordered,
  className,
  striped,
}) => {
  return (
    <TrussTable bordered={bordered} className={className} striped={striped}>
      {children}
    </TrussTable>
  );
};

export default Table;
