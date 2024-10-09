import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setUser } from '../../redux/slices/auth.slice';
import { useLoginUserMutation } from '../../redux/api/auth.api';
import { useForm } from 'react-hook-form';
import { Navigate, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { RootState } from '../../redux/store';
import style from './auth.module.sass';
import classNames from 'classnames';
import { Alert, IconButton, TextField } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';

interface LoginData {
    login: string;
    password: string;
}

const Auth: React.FC = () => {
    const [
        loginUser,
        {
            data: loginData,
            isSuccess: isLoginSuccess,
            isLoading: isLoginLoading,
            isError: isLoginError,
            error: loginError,
        },
    ] = useLoginUserMutation();
    const {
        register,
        handleSubmit,
        setError,
        formState: { errors },
        clearErrors,
    } = useForm();
    const [showPassword, setShowPassword] = useState(false);
    const { isAuth } = useSelector((state: RootState) => state.authSlice);
    const navigate = useNavigate();
    const dispatch = useDispatch();

    useEffect(() => {
        if (isLoginSuccess) {
            dispatch(setUser(loginData));
            navigate('/dashboard');
        }
        if (isLoginError) {
            setError('password', { type: 'focus' }, { shouldFocus: true });
            setError('login', { type: 'focus' }, { shouldFocus: true });
            setError('auth', { type: 'focus' }, { shouldFocus: true });
        }
    }, [isLoginLoading, isLoginSuccess]);

    if (isAuth) {
        return <Navigate to="/dashboard" replace />;
    }

    const onSubmit = async (data: LoginData) => {
        clearErrors('auth');
        const { login, password } = data;
        if (login && password) await loginUser({ login, password });
    };

    const handleClickShowPassword = () => setShowPassword((show) => !show);
    const handleMouseDownPassword = (event) => {
        event.preventDefault();
    };

    return (
        <>
            <div className={style.auth}>
                <form
                    onSubmit={handleSubmit(onSubmit)}
                    className={classNames(style.auth__form)}
                >
                    <div>
                        <h2>Вход в систему</h2>
                    </div>
                    <TextField
                        {...register('login', {
                            required: 'Введите логин',
                        })}
                        label="Логин"
                        id="login"
                        variant="outlined"
                        type="text"
                        error={!!errors.login}
                        helperText={errors.login ? errors.login.message : false}
                    />
                    <TextField
                        {...register('password', {
                            required: 'Введите пароль',
                        })}
                        label="Пароль"
                        id="password"
                        variant="outlined"
                        type={showPassword ? 'text' : 'password'}
                        error={!!errors.password}
                        helperText={
                            errors.password ? errors.password.message : false
                        }
                        InputProps={{
                            endAdornment: (
                                <IconButton
                                    aria-label="toggle password visibility"
                                    onClick={handleClickShowPassword}
                                    onMouseDown={handleMouseDownPassword}
                                >
                                    {showPassword ? (
                                        <Visibility />
                                    ) : (
                                        <VisibilityOff />
                                    )}
                                </IconButton>
                            ),
                        }}
                    />
                    {errors.auth && (
                        <Alert variant="filled" severity="error">
                            {errors.auth.message}
                        </Alert>
                    )}
                    <LoadingButton
                        size="large"
                        type="submit"
                        loading={isLoginLoading}
                        variant="outlined"
                        onClick={() => onSubmit()}
                        disabled={isLoginLoading}
                    >
                        <b>Войти</b>
                    </LoadingButton>
                </form>
            </div>
        </>
    );
};

export default Auth;
