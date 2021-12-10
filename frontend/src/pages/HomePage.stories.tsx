/* eslint-disable react/jsx-props-no-spreading */
import React from 'react';
import { Story, Meta } from '@storybook/react';
import StoryRouter from 'storybook-react-router';
import Patient from 'types/Patient';
import { DefaultLayout } from 'components/PageLayout.stories';
import PageLayout, { PageLayoutProps } from 'components/PageLayout';
import { GET_PATIENT_ON_PATHWAY_CONNECTION_QUERY } from 'app/queries/UsePatientsForPathway';
import { DecisionPointType } from 'types/DecisionPoint';
import { currentPathwayId } from 'app/cache';
import HomePage, { HomePageProps } from './HomePage';

// Dummy data for display
const patientArray: Patient[] = [];
const patient = {
  hospitalNumber: 'MRN1234567',
  firstName: 'John',
  lastName: 'Doe',
};

for (let i = 0; i < 20; ++i) {
  const newPatient = {
    id: i,
    hospitalNumber: `${patient.hospitalNumber}-${i + 1}`,
    firstName: patient.firstName,
    lastName: `${patient.lastName} ${i + 1}`,
  };
  patientArray.push(newPatient);
}

const edges = patientArray.map((p) => ({
  cursor: `${p.id}YXJyYXljb25uZWN0aW9uOjA=`,
  node: p,
}));
const patientsPerPage = 10;

export default {
  title: 'Pages/Home Page',
  component: HomePage,
  decorators: [
    (HomePageStory) => (
      <PageLayout { ...DefaultLayout.args as PageLayoutProps }>
        <HomePageStory />
      </PageLayout>
    ),
  ],
} as Meta<typeof HomePage>;

export const Default: Story<HomePageProps> = (args: HomePageProps) => {
  currentPathwayId(1);
  return <HomePage { ...args } />;
};
Default.args = { patientsPerPage: patientsPerPage };
Default.parameters = {
  apolloClient: {
    mocks: [
      { // TRIAGE DATA
        request: {
          query: GET_PATIENT_ON_PATHWAY_CONNECTION_QUERY,
          variables: {
            pathwayId: 1,
            first: patientsPerPage,
            awaitingDecisionType: DecisionPointType.TRIAGE,
          },
        },
        result: {
          data: {
            getPatientOnPathwayConnection: {
              totalCount: edges.length,
              edges: edges.slice(0, patientsPerPage),
              pageInfo: {
                hasNextPage: true,
                endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              },
            },
          },
        },
      },
      { // TRIAGE PAGE 2
        request: {
          query: GET_PATIENT_ON_PATHWAY_CONNECTION_QUERY,
          variables: {
            pathwayId: 1,
            first: patientsPerPage,
            awaitingDecisionType: DecisionPointType.TRIAGE,
            after: 'YXJyYXljb25uZWN0aW9uOjA=',
          },
        },
        result: {
          data: {
            getPatientOnPathwayConnection: {
              totalCount: edges.length,
              edges: edges.slice(11, patientsPerPage),
              pageInfo: {
                hasNextPage: false,
                endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              },
            },
          },
        },
      },
      { // CLINIC DATA
        request: {
          query: GET_PATIENT_ON_PATHWAY_CONNECTION_QUERY,
          variables: {
            pathwayId: 1,
            first: patientsPerPage,
            awaitingDecisionType: DecisionPointType.CLINIC,
          },
        },
        result: {
          data: {
            getPatientOnPathwayConnection: {
              totalCount: edges.length,
              edges: edges.slice(0, patientsPerPage),
              pageInfo: {
                hasNextPage: true,
                endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              },
            },
          },
        },
      },
      { // CLINIC PAGE 2
        request: {
          query: GET_PATIENT_ON_PATHWAY_CONNECTION_QUERY,
          variables: {
            pathwayId: 1,
            first: patientsPerPage,
            after: 'YXJyYXljb25uZWN0aW9uOjA=',
            awaitingDecisionType: DecisionPointType.CLINIC,
          },
        },
        result: {
          data: {
            getPatientOnPathwayConnection: {
              totalCount: edges.length,
              edges: edges.slice(5, patientsPerPage),
              pageInfo: {
                hasNextPage: false,
                endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              },
            },
          },
        },
      },
    ],
  },
};
