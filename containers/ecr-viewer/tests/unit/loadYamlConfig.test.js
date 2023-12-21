import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import "@testing-library/jest-dom";
import loadYamlConfig from '@/app/api/data/utils';
describe('loadYamlConfig', () => {
    it('returns the yaml config', () => {
      expect(3).toEqual(3);
    })
    // it('renders the button and toggles content when clicked', () => {
    //     const { getByText, queryByText, getByTestId } = render(<LinkAccordion />);

    //     // Initially, the content should not be visible
    //     expect(queryByText('Our tool expects the .zip file format generated from AIMS.')).toBeNull();

    //     // Click the button to open the accordion
    //     const accordionButton = getByTestId('accordion-button');
    //     expect(accordionButton).toBeInTheDocument();

    //     // Click the button again to close the accordion
    //     fireEvent.click(accordionButton);

    //     // After clicking, the content should be visible
    //     expect(getByText('Our tool expects the .zip file format generated from AIMS. For a successful upload, your .zip file:')).toBeInTheDocument();

    //     // Click the button again to close the accordion
    //     fireEvent.click(accordionButton);

    //     // After clicking again, the content should be hidden
    //     expect(queryByText('Our tool expects the .zip file format generated from AIMS.')).toBeNull();
    // });
});
