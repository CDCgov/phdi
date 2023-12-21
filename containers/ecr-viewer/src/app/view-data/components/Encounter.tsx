import { DisplayData } from "@/app/utils";

interface SocialHistoryProps {
    encounterData: DisplayData[],
    providerData: DisplayData[]
}

const Encounter = (
    { encounterData, providerData }: SocialHistoryProps
) => {
    const renderData = (item: any, index: number) => {
        return (
            <div key={index}>
                <div className="grid-row">
                    <div className="data-title"><h4>{item.title}</h4></div>
                    <div className="grid-col-auto">
                        {item.value}
                    </div>
                </div>
                <div className={"section__line_gray"} />
            </div>
        )
    }

    return (
        <div>
            <div
                className="padding-bottom-3"
                aria-labelledby="summary-box-key-information"
            >
                <div className="usa-summary-box__body">
                    <h3
                        className="usa-summary-box__heading padding-y-105"
                        id="summary-box-key-information"
                    >
                        Encounter Details
                    </h3>
                    <div className="usa-summary-box__text">
                        {encounterData.map((item, index) => renderData(item, index))}
                    </div>
                    <h3
                        className="usa-summary-box__heading padding-y-105"
                        id="summary-box-key-information"
                    >
                        Provider Details
                    </h3>
                    <div className="usa-summary-box__text">
                        {providerData.map((item, index) => renderData(item, index))}
                    </div>
                </div>
            </div>
        </div>);
};

export default Encounter;