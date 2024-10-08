import { useDispatch, useSelector } from 'react-redux';
import { setUser } from '../../redux/slices/auth.slice';
import { useLoginUserMutation } from '../../redux/api/auth.api';
import { useForm } from 'react-hook-form';
import { Navigate, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { RootState } from '../../redux/store';

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

    return (
        <div>
            <p>AUTH</p>
            <button
                onClick={() =>
                    dispatch(
                        setUser({
                            displayName: 'Владислав Влазнев',
                        })
                    )
                }
            >
                CLICK TO AUTH
            </button>
        </div>
    );
};

export default Auth;
