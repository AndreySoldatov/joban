import React from "react";
import { useSelector } from "react-redux";
import { useRegisterUserMutation } from "../../redux/api/auth.api";
import { SubmitHandler, useForm } from "react-hook-form";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { RootState } from "../../redux/store";
import style from "./auth.module.sass";
import classNames from "classnames";
import { IconButton, TextField } from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { LoadingButton } from "@mui/lab";
import { toast } from "react-toastify";

interface RegisterData {
    login: string;
    password: string;
    firstName: string;
    lastName: string;
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
        formState: { errors },
    } = useForm<RegisterData>();
    const [showPassword, setShowPassword] = useState(false);
    const { isAuth } = useSelector((state: RootState) => state.authSlice);
    const navigate = useNavigate();

    const notifyError = (message?: string) =>
        toast.error(message || "Что-то пошло не так...");

    useEffect(() => {
        if (isRegisterSuccess) {
            navigate("/login", { state: { isRegisterSuccess } });
        }
        if (isRegisterError) {
            notifyError();
        }
    }, [isRegisterError, isRegisterSuccess]);

    if (isAuth) {
        return (
            <Navigate
                to="/dashboard"
                replace
            />
        );
    }

    const onSubmit: SubmitHandler<RegisterData> = async (
        data: RegisterData
    ) => {
        const { login, password, firstName, lastName } = data;
        if (login && password && firstName && lastName)
            await registerUser({ login, password, firstName, lastName });
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
                        {...register("firstName", {
                            required: "Введите имя",
                            pattern: {
                                value: /^[а-яА-Я]+$/,
                                message:
                                    "Имя может содержать только буквы русского алфовита",
                            },
                        })}
                        label="Имя"
                        id="firstName"
                        variant="outlined"
                        type="text"
                        error={!!errors.firstName}
                        helperText={
                            errors.firstName &&
                            typeof errors.firstName?.message === "string" &&
                            errors.firstName?.message
                        }
                    />
                    <TextField
                        {...register("lastName", {
                            required: "Введите фамилию",
                            pattern: {
                                value: /^[а-яА-Я]+$/,
                                message:
                                    "Фамилия может содержать только буквы русского алфовита",
                            },
                        })}
                        label="Фамилия"
                        id="secondName"
                        variant="outlined"
                        type="text"
                        error={!!errors.lastName}
                        helperText={
                            errors.lastName &&
                            typeof errors.lastName?.message === "string" &&
                            errors.lastName?.message
                        }
                    />
                    <TextField
                        {...register("login", {
                            required: "Введите логин",
                            pattern: {
                                value: /^[a-zA-Z0-9.]+$/,
                                message:
                                    "Логин может содержать только латинские буквы, цифры и точку",
                            },
                        })}
                        label="Логин"
                        id="login"
                        variant="outlined"
                        type="text"
                        error={!!errors.login}
                        helperText={
                            errors.login?.message &&
                            typeof errors.login?.message === "string" &&
                            errors.login?.message
                        }
                    />
                    <TextField
                        {...register("password", {
                            required: "Введите пароль",
                        })}
                        label="Пароль"
                        id="password"
                        variant="outlined"
                        type={showPassword ? "text" : "password"}
                        error={!!errors.password}
                        helperText={
                            errors.password?.message &&
                            typeof errors.password?.message === "string" &&
                            errors.password?.message
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
                    <LoadingButton
                        size="large"
                        type="submit"
                        loading={isRegisterLoading}
                        variant="outlined"
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
