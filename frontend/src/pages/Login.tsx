import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { pathwayOptionsVar, loggedInUserVar, currentPathwayId } from 'app/cache';
import User from 'types/Users';
import PathwayOption from 'types/PathwayOption';

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface LoginPageProps { }

export type LoginData = {
  user: User | null;
  pathways: PathwayOption[] | null;
  error: string;
};

export interface LoginFormInputs {
  username: string;
  password: string;
}

type LoginSubmitHook = [
  boolean,
  any,
  LoginData | undefined,
  (variables: LoginFormInputs) => void
];

export function useLoginSubmit(): LoginSubmitHook {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<unknown>(undefined);
  const [data, setData] = useState<LoginData | undefined>(undefined);

  async function doLogin(variables: LoginFormInputs) {
    setLoading(true);
    try {
      const response = await window.fetch('http://localhost:8080/rest/login', {
        method: 'POST',
        headers: {
          'content-type': 'application/json;charset=UTF-8',
        },
        body: JSON.stringify(variables),
      });
      if (!response.ok) {
        throw new Error(`Error: Response ${response.status} ${response.statusText}`);
      }
      const decoded: LoginData = await response.json();
      if (decoded.error) {
        setError({ message: decoded.error }); // e.g. invalid password
      } else {
        setData(decoded);
      }
    } catch (err) {
      setError(err);
    }
    setLoading(false);
  }
  return [loading, error, data, doLogin];
}

function loginSuccess({ user, pathways }: LoginData) {
  // Here were going to cast to avoid the nulls because this will only be called
  // in success because that's what this function is named, right?
  loggedInUserVar(user as User);
  const paths = pathways as PathwayOption[];
  pathwayOptionsVar(paths);
  currentPathwayId(paths[0].id);
}

const LoginPage = (): JSX.Element => {
  const [loading, error, data, doLogin] = useLoginSubmit();

  const loginSchema = yup.object({
    username: yup.string().required(),
    password: yup.string().required(),
  }).required();

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<LoginFormInputs>({ resolver: yupResolver(loginSchema) });
  const navigate = useNavigate();
  useEffect(() => {
    if (!error && data?.user && data?.pathways) {
      loginSuccess(data);
      navigate('/', { replace: true });
    }
  });

  return (
    <div>
      <section>
        <div className="container py-5 h-100">
          <div className="row d-flex justify-content-center align-items-center h-100">
            <div className="card shadow-2-strong col-12 col-sm-12 col-md-10 col-lg-7 col-xl-5 mb-5">
              <form onSubmit={ handleSubmit( () => {
                doLogin(getValues());
              } ) }
              >
                <fieldset disabled={ loading } aria-label="Login Form">
                  <div className="form-group mb-2">
                    <h5>Please enter credentials below to access Spiritum Duo</h5>
                  </div>

                  <div className="form-group row mb-2">
                    <label className="col-sm-9 col-form-label" htmlFor="username">Username
                      <input id="username" type="text" placeholder="Username" className="form-control" { ...register('username', { required: true }) } />
                      <p>{ errors.username?.message }</p>
                    </label>
                  </div>

                  <div className="form-group row mb-4">
                    <label className="col-sm-9 col-form-label" htmlFor="password">Password
                      <input id="password" type="password" placeholder="Password" className="form-control" { ...register('password', { required: true }) } />
                      <p>{ errors.password?.message }</p>
                    </label>
                  </div>
                  <p>{ error?.message }</p>
                  <p>{ loading ? 'Loading' : '' }</p>
                  <button type="submit" className="btn btn-outline-secondary float-end ms-1">Login</button>
                </fieldset>
              </form>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LoginPage;
