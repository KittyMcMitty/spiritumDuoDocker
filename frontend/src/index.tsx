import React from 'react';
import ReactDOM from 'react-dom';
import { onError } from '@apollo/client/link/error';
import { ApolloClient, ApolloProvider, HttpLink, from } from '@apollo/client';
import { cache } from 'app/cache';
import './index.css';
import App from 'app/App';
import reportWebVitals from 'reportWebVitals';

// TODO: Disable this for production! This is just because we are on a different port
const link = new HttpLink({ uri: 'http://localhost:8080/graphql' });

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.log(`[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`);
    });
  }

  if (networkError) console.log(`[Network error]: ${networkError}`);
});

const client = new ApolloClient({
  link: from([errorLink, link]),
  cache: cache,
  connectToDevTools: true,
});

ReactDOM.render(
  <React.StrictMode>
    <ApolloProvider client={ client }>
      <App />
    </ApolloProvider>
  </React.StrictMode>,
  // eslint-disable-next-line no-undef
  document.getElementById('root'),
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
