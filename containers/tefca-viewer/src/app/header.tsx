"use client";

import Image from "next/image";
import { useRef } from "react";
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
            <Image
              src="/tefca-viewer/DIBBs_logo.png"
              alt="DIBBs Logo"
              width={211}
              height={43}
              className="usa-footer__logo-img"
            />
            <div className="usa-logo" style={{ marginLeft: "16px" }}>
              <em className="usa-logo__text text-base-lightest">
                <a
                  className="text-base-lightest font-sans-lg text-bold"
                  href="/tefca-viewer"
                  title="Pipeline Demo Site"
                >
                  Pipeline Demo Site
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
            <ModalToggleButton
              modalRef={modalRef}
              opener
              style={{ cursor: "pointer" }}
            >
              Data Usage Policy
            </ModalToggleButton>
          </div>
        </div>
      </header>

      <Modal
        ref={modalRef}
        id="data-usage-policy-modal"
        aria-labelledby="data-usage-policy-modal-heading"
        aria-describedby="data-usage-policy-modal-description"
        isInitiallyOpen={false}
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
    </>
  );
}
