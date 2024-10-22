import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from './redux/store';
import { Navigate, Route, Routes } from 'react-router-dom';
import { PrivateRoute } from './utils/PrivateRoute';
import Auth from './pages/Auth/Auth';
import Dashboard from './pages/Dashboard/Dashboard';
import Spinner from './components/Spinner/Spinner';
import { useEffect, useState } from 'react';
import { skipToken } from '@reduxjs/toolkit/query';
import { useWhoAmIQuery } from './redux/api/auth.api';
import { resetUser, setUser } from './redux/slices/auth.slice';
import Register from './pages/Auth/Register';

type WhoAmIState = boolean | typeof skipToken;

const App: React.FC = () => {
    const dispatch = useDispatch();
    const { isAuth, isWhoAmIChecked } = useSelector(
        (state: RootState) => state.authSlice
    );
    const [state, setState] = useState<{ whoAmI: WhoAmIState }>({
        whoAmI: skipToken,
    });
    const { whoAmI } = state;

    const {
        data: whoAmIData,
        isSuccess: isWhoAmISuccess,
        isError: isWhoAmIError,
        error: whoAmIError,
    } = useWhoAmIQuery(whoAmI);

    useState(() => {
        setState({ ...state, whoAmI: true });
    });
    useEffect(() => {
        if (isWhoAmIError) {
            if ('status' in whoAmIError) {
                if (whoAmIError.status === 401) {
                    dispatch(resetUser());
                }
            }
        }
        if (isWhoAmISuccess) dispatch(setUser(whoAmIData));
    }, [isWhoAmIError, isWhoAmISuccess]);

    // if (!isWhoAmIChecked) {
    //     return <Spinner />;
    // }

    return (
        <Routes>
            <Route
                path="/"
                element={
                    isAuth ? (
                        <Navigate to="/dashboard" replace />
                    ) : (
                        <Navigate to="/login" replace />
                    )
                }
            />
            <Route path="/login" element={<Auth />} />
            <Route path="/register" element={<Register />} />
            <Route element={<PrivateRoute isAuth={isAuth} />}>
                <Route path="/dashboard" element={<Dashboard />} />
            </Route>
        </Routes>
    );
};

export default App;
