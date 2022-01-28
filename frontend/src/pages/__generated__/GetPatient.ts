/* tslint:disable */
/* eslint-disable */
// @generated
// This file was automatically generated and should not be edited.

import { PatientCommunicationMethods } from "./../../../__generated__/globalTypes";

// ====================================================
// GraphQL query operation: GetPatient
// ====================================================

export interface GetPatient_getPatient_onPathways_decisionPoints_milestones {
  __typename: "Milestone";
  currentState: string;
}

export interface GetPatient_getPatient_onPathways_decisionPoints {
  __typename: "DecisionPoint";
  clinicHistory: string;
  comorbidities: string;
  milestones: GetPatient_getPatient_onPathways_decisionPoints_milestones[] | null;
}

export interface GetPatient_getPatient_onPathways {
  __typename: "OnPathway";
  id: string;
  decisionPoints: GetPatient_getPatient_onPathways_decisionPoints[] | null;
}

export interface GetPatient_getPatient {
  __typename: "Patient";
  hospitalNumber: string;
  id: string;
  communicationMethod: PatientCommunicationMethods;
  firstName: string;
  lastName: string;
  dateOfBirth: any;
  onPathways: GetPatient_getPatient_onPathways[] | null;
}

export interface GetPatient_getMilestoneTypes {
  __typename: "MilestoneType";
  id: string;
  name: string;
}

export interface GetPatient {
  getPatient: GetPatient_getPatient | null;
  getMilestoneTypes: GetPatient_getMilestoneTypes[] | null;
}

export interface GetPatientVariables {
  hospitalNumber?: string | null;
  pathwayId?: string | null;
}
