import { Navigate, Outlet } from 'react-router-dom';

interface PrivateRouteProps {
    isAuth: boolean;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ isAuth }) => {
    return isAuth ? <Outlet /> : <Navigate to="/login" replace />;
};
