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

/**
 * Modal wrapper around the Truss modal
 * @param param0 - props
 * @param param0.id - ID for labeling / referencing the various subcomponents in
 * the modal
 * @param param0.heading - Modal heading
 * @param param0.description - Modal body
 * @param param0.modalRef - ref object to connect the toggle button with the
 * actual modal.
 * @returns A modal component
 */
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
/**
 * Modal button trigger the opening of a modal
 * @param param0 params
 * @param param0.modalRef - Ref object to connect button to the parent modal instance
 * @param param0.title - What text to display on the button
 * @param param0.className - optional styling classes
 * @returns A modal button that should open the modal
 */
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
