import React from 'react';
import { useSelector } from 'react-redux';
import { useRegisterUserMutation } from '../../redux/api/auth.api';
import { useForm } from 'react-hook-form';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { RootState } from '../../redux/store';
import style from './auth.module.sass';
import classNames from 'classnames';
import { Alert, IconButton, TextField } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import { toast } from 'react-toastify';

interface LoginData {
    login: string;
    password: string;
}

const Register: React.FC = () => {
    const [
        registerUser,
        {
            isSuccess: isRegisterSuccess,
            isLoading: isRegisterLoading,
            isError: isRegisterError,
        },
    ] = useRegisterUserMutation();
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

    const notifyError = (message?: string) =>
        toast.error(message || 'Что-то пошло не так...');

    useEffect(() => {
        if (isRegisterSuccess) {
            navigate('/login', { state: { isRegisterSuccess } });
        }
        if (isRegisterError) {
            notifyError();
            setError('password', { type: 'focus' }, { shouldFocus: true });
            setError('login', { type: 'focus' }, { shouldFocus: true });
            setError('auth', { type: 'focus' }, { shouldFocus: true });
        }
    }, [isRegisterError, isRegisterSuccess]);

    if (isAuth) {
        return <Navigate to="/dashboard" replace />;
    }

    const onSubmit = async (data: LoginData) => {
        clearErrors('auth');
        const { login, password } = data;
        if (login && password) await registerUser({ login, password });
    };

    const handleClickShowPassword = () => setShowPassword((show) => !show);
    const handleMouseDownPassword = (
        event: React.MouseEvent<HTMLButtonElement>
    ) => {
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
                        <h2>Регистрация</h2>
                    </div>
                    <TextField
                        {...register('login', {
                            required: 'Введите логин',
                            pattern: {
                                value: /^[a-zA-Z0-9.]+$/,
                                message:
                                    'Логин может содержать только латинские буквы, цифры и точку',
                            },
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
                        loading={isRegisterLoading}
                        variant="outlined"
                        onClick={() => onSubmit()}
                        disabled={isRegisterLoading}
                    >
                        <b>Зарегистрироваться</b>
                    </LoadingButton>
                </form>
                <Link to="/login">Есть аккаунт?</Link>
            </div>
        </>
    );
};

export default Register;
