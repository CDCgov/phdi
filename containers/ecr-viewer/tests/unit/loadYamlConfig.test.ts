import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import "@testing-library/jest-dom";
import {loadYamlConfig} from '../../src/app/api/fhir-data/utils';


describe('loadYamlConfig', () => {
    it('returns the yaml config', () => {
      const config = loadYamlConfig();
      expect(Object.keys(config).length).toBeGreaterThan(3)
      expect(config["patientGivenName"]).toBe("Bundle.entry.resource.where(resourceType = 'Patient').name.first().given")
    })
    
});
