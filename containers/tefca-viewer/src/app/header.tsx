"use client";

import Image from "next/image";
import { useState } from "react";

/**
 * Produces the header.
 * @returns The HeaderComponent component.
 */
export default function HeaderComponent() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
  };

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
            <p
              className="text-base-lightest"
              onClick={toggleModal}
              style={{ cursor: "pointer" }}
            >
              Data Usage Policy
            </p>
          </div>
        </div>
      </header>

      {isModalOpen && (
        <div className="usa-modal is-visible" id="data-usage-policy-modal">
          <div className="usa-modal__content">
            <div className="usa-modal__main">
              <h2 className="usa-modal__heading">How is my data stored?</h2>
              <p>
                It's not! Data inputted into the TEFCA Query Connector is not
                persisted or stored anywhere.
              </p>
              <button
                type="button"
                className="usa-button"
                onClick={toggleModal}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
