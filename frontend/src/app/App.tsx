import 'bootstrap/dist/css/bootstrap.min.css';
// Bootstrap imports first so other modules can override
import React from 'react';
import { BrowserRouter, Link, Redirect, Route, Switch } from 'react-router-dom';
import LoginController from 'app/controllers/LoginController';
import { pathwayOptionsVar, loggedInUserVar } from 'app/cache';
import LoginModelImpl from 'app/models/LoginModel';
import LoginPage from 'pages/Login';
import { useReactiveVar } from '@apollo/client';
import logo from './logo.svg';
import './App.css';

const App = (): JSX.Element => (
  <BrowserRouter>
    <Switch>
      <Route path="/login">
        { LoginController(LoginModelImpl, LoginPage) }
      </Route>
      <Route path="/logout">
        <Logout />
      </Route>
      <LoggedInRoute>
        <Route path="/">
          <HomeDemo />
        </Route>
      </LoggedInRoute>
    </Switch>
  </BrowserRouter>
);

const HomeDemo = () => {
  const user = useReactiveVar(loggedInUserVar);
  const pathways = useReactiveVar(pathwayOptionsVar);
  return (
    <>
      <div className="App">
        <header className="App-header">
          <img src={ logo } className="App-logo" alt="logo" />
          <p>
            {/* eslint-disable-next-line react/jsx-one-expression-per-line */}
            Edit <code>src/App.tsx</code> and save to reload.
          </p>
          <a
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React - boo
          </a>
          <h5><Link to="/logout">Logout</Link></h5>
          <h5>User: {JSON.stringify(user)}</h5>
          <h5>Pathway: {JSON.stringify(pathways)}</h5>
        </header>
      </div>
    </>
  );
};

const Logout = () => {
  loggedInUserVar(undefined);
  pathwayOptionsVar(undefined);
  return (<Redirect to="/" />);
};

const LoggedInRoute = ({ children, ...props }: React.ComponentPropsWithRef<any>): JSX.Element => {
  const loggedIn = (loggedInUserVar() !== undefined) && (pathwayOptionsVar() !== undefined);
  return (
    <Route
      // eslint-disable-next-line react/jsx-props-no-spreading
      { ...props }
      render={ ({ location }) => (
        loggedIn
          ? children
          : (
            <Redirect to={ {
              pathname: '/login',
              state: { from: location },
            } }
            />
          )
      ) }
    />
  );
};

export default App;
