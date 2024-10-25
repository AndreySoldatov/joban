import React from 'react';
import { Navigate } from 'react-router-dom';

interface Props {
    route: string;
    isAuth: boolean;
}

const RedirectRoute: React.FC<Props> = ({ route, isAuth }) => {
    return <Navigate to={`/${isAuth ? route : 'login'}`} replace />;
};

export default RedirectRoute;
