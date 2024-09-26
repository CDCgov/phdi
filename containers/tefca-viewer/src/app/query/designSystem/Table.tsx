import { Table as TrussTable } from "@trussworks/react-uswds";

type TableProps = {
  children: React.ReactNode;
  className?: string;
  bordered?: boolean;
  striped?: boolean;
};

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
