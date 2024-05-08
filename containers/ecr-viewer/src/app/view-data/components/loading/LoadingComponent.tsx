/**
 * Temp
 * @returns The main eCR Viewer JSX component.
 */
export const EcrLoading = () => {
  const renderEcrSummaryFiller = (numberOfRows: number) => {
    // Create an array of specified size to map over
    const rows = Array.from({ length: numberOfRows });

    // Map over the array to create multiple divs
    return (
      <>
        {rows.map((_, index) => (
          <div key={index}>
            <div className="grid-row">
              <div className="grid-col-4">
                <div className="loading-blob margin-right-1">&nbsp;</div>
              </div>
              <div className="grid-col-8 loading-blob">&nbsp;</div>
            </div>
            <div className="section__line" />
          </div>
        ))}
      </>
    );
  };

  return (
    <div>
      <div className="main-container">
        <div className="content-wrapper">
          <div className={"ecr-viewer-container"}>
            <div className="ecr-content">
              <h2 className="margin-bottom-3" id="ecr-summary">
                eCR Summary
              </h2>
              <div className={"info-container"}>
                <div
                  className="usa-summary-box padding-3"
                  aria-labelledby="summary-box-key-information"
                >
                  <h3 className="summary-box-key-information side-nav-ignore">
                    About the Patient
                  </h3>
                  {renderEcrSummaryFiller(4)}
                  <h3 className="summary-box-key-information side-nav-ignore">
                    About the Encounter
                  </h3>
                  {renderEcrSummaryFiller(4)}
                  <h3 className="summary-box-key-information side-nav-ignore">
                    About the Condition
                  </h3>
                  {renderEcrSummaryFiller(4)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
