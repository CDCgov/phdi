"use client";

// import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import {
  Modal,
  ModalHeading,
  ModalFooter,
  ButtonGroup,
  ModalToggleButton,
} from "@trussworks/react-uswds";

/**
 * Produces the header.
 * @returns The HeaderComponent component.
 */
export default function HeaderComponent() {
  const modalRef = useRef(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <>
      <header className="usa-header usa-header--basic bg-primary-darker">
        <div
          className="header-footer-content usa-nav-container"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center" }}>
            {/* <a href="/tefca-viewer" title="TEFCA Viewer">
              <Image
                src="/tefca-viewer/DIBBs_logo.png"
                alt="DIBBs Logo"
                width={168}
                height={34}
                className="usa-header__logo-img"
              />
            </a> */}
            <div className="usa-logo" style={{ marginLeft: "16px" }}>
              <em className="usa-logo__text text-base-lightest">
                <a
                  className="text-base-lightest font-sans-xl text-bold"
                  href="/tefca-viewer"
                  title="TEFCA Viewer"
                >
                  TEFCA Viewer
                </a>
              </em>
            </div>
          </div>
          <div
            style={{
              whiteSpace: "nowrap",
              textAlign: "right",
              marginLeft: "auto",
            }}
          >
            {isClient && (
              <ModalToggleButton
                modalRef={modalRef}
                opener
                className="text-base-lightest"
                style={{
                  cursor: "pointer",
                  background: "none",
                  border: "none",
                  color: "inherit",
                  padding: 0,
                  font: "inherit",
                }}
                title="Data Usage Policy"
              >
                Data Usage Policy
              </ModalToggleButton>
            )}
          </div>
        </div>
      </header>

      {isClient && (
        <Modal
          ref={modalRef}
          id="data-usage-policy-modal"
          aria-labelledby="data-usage-policy-modal-heading"
          aria-describedby="data-usage-policy-modal-description"
          isInitiallyOpen={false}
          placeholder={undefined}
          onPointerEnterCapture={undefined}
          onPointerLeaveCapture={undefined}
        >
          <ModalHeading id="data-usage-policy-modal-heading">
            How is my data stored?
          </ModalHeading>
          <div className="usa-prose">
            <p id="data-usage-policy-modal-description">
              It's not! Data inputted into the TEFCA Query Connector is not
              persisted or stored anywhere.
            </p>
          </div>
          <ModalFooter>
            <ButtonGroup>
              <ModalToggleButton modalRef={modalRef} closer>
                Close
              </ModalToggleButton>
            </ButtonGroup>
          </ModalFooter>
        </Modal>
      )}
    </>
  );
}
