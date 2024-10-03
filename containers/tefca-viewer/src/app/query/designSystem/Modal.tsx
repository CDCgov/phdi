import {
  Modal as TrussModal,
  ModalHeading,
  ModalFooter,
  ButtonGroup,
  ModalToggleButton,
  ModalRef,
} from "@trussworks/react-uswds";
import { RefObject } from "react";

type ModalProps = {
  heading: string;
  description: string;
  id: string;
  modalRef: RefObject<ModalRef>;
  // expand this to support more interesting button use cases when needed
};
export const Modal: React.FC<ModalProps> = ({
  id,
  heading,
  description,
  modalRef,
}) => {
  return (
    <TrussModal
      ref={modalRef}
      id={`${id}-modal`}
      aria-labelledby={`${id}-modal-heading`}
      aria-describedby={`${id}-modal-description`}
    >
      <ModalHeading id={`${id}-modal-heading`}>{heading}</ModalHeading>
      <div className="usa-prose">
        <p id={`${id}-modal-description`}>{description}</p>
      </div>
      <ModalFooter>
        <ButtonGroup>
          <ModalToggleButton modalRef={modalRef} closer>
            Close
          </ModalToggleButton>
        </ButtonGroup>
      </ModalFooter>
    </TrussModal>
  );
};

type ModalButtonProps = {
  modalRef: RefObject<ModalRef>;
  title: string;
  className?: string;
};
export const ModalButton: React.FC<ModalButtonProps> = ({
  modalRef,
  title,
  className,
}) => {
  return (
    <ModalToggleButton
      modalRef={modalRef}
      opener
      className={className}
      title={title}
    >
      {title}
    </ModalToggleButton>
  );
};
