import { useState } from 'react';
import { ApolloError, gql, useMutation } from '@apollo/client';
import { pathwayOptionsVar, loggedInUserVar, currentPathwayId } from 'app/cache';
import User from 'types/Users';
import * as yup from 'yup';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';

export enum LoginStatus {
  SUCCESS,
  INVALID_LOGIN,
  INITIAL,
  LOADING
}

export interface LoginFormInputs {
  username: string;
  password: string;
}

type LoginStatusHook = {
  status: LoginStatus;
  setLoginStatus: (status: LoginStatus) => void;
};

export function useLoginStatus(): LoginStatusHook {
  const [status, setStatus] = useState(LoginStatus.INITIAL);
  function setLoginStatus(loginStatus: LoginStatus) {
    setStatus(loginStatus);
  }
  return {
    status: status,
    setLoginStatus: setLoginStatus,
  };
}

type LoginSubmitHook = [
  boolean,
  ApolloError | undefined, any,
  (variables: LoginFormInputs) => void
];

export const LOGIN_QUERY = gql`
mutation login ($username: String!, $password: String!) {
  login (username: $username, password: $password) {
        id
        firstName
        lastName
        username
        department
    }
  }`;

export function useLoginSubmit(): LoginSubmitHook {
  function doLogin(variables: LoginFormInputs) {
    loginMutation({ variables: variables });
  }
  const [loginMutation, { loading, error, data }] = useMutation(LOGIN_QUERY);

  return [loading, error, data, doLogin];
}

type LoginData = {
  user: User;
};

export function loginSuccess({ user }: LoginData) {
  loggedInUserVar(user);
  pathwayOptionsVar([
    { id: 1, name: 'Lung Cancer' },
    { id: 2, name: 'Bronceastasis' },
  ]);
  currentPathwayId(1);
}

export function useLoginForm() {
  const loginSchema = yup.object({
    username: yup.string().required(),
    password: yup.string().required(),
  }).required();

  return useForm<LoginFormInputs>({ resolver: yupResolver(loginSchema) });
}
