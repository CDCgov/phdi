import { Table as TrussTable } from "@trussworks/react-uswds";

type TableProps = {
  children: React.ReactNode;
  className?: string;
  bordered?: boolean;
  striped?: boolean;
};

/**
 *
 * @param root0
 * @param root0.children
 * @param root0.bordered
 * @param root0.className
 * @param root0.striped
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
