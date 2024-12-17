import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "./redux/store";
import {
    createBrowserRouter,
    createRoutesFromElements,
    Navigate,
    Route,
    RouterProvider,
} from "react-router-dom";
import { PrivateRoute } from "./utils/PrivateRoute";
import Auth from "./pages/Auth/Auth";
import Dashboard from "./pages/Dashboard/Dashboard";
import { useEffect } from "react";
import { useWhoAmIQuery } from "./redux/api/auth.api";
import { resetUser, setUser } from "./redux/slices/auth.slice";
import Register from "./pages/Auth/Register";
import Layout from "./layout/Layout";
import RedirectRoute from "./utils/RedirectRoute";
import Boards from "./pages/Boards/Boards";
import Board from "./pages/Boards/Board";
import BoardNew from "./pages/Boards/BoardNew";
import Spinner from "./components/Spinner/Spinner";
import Task from "./pages/Task/Task";
import { Box } from "@mui/material";

const App: React.FC = () => {
    const dispatch = useDispatch<AppDispatch>();
    const { isAuth, isWhoAmIChecked } = useSelector(
        (state: RootState) => state.authSlice
    );
    const {
        data: whoAmIData,
        isSuccess: isWhoAmISuccess,
        isError: isWhoAmIError,
    } = useWhoAmIQuery();

    useEffect(() => {
        if (isWhoAmIError) {
            dispatch(resetUser());
        }
        if (isWhoAmISuccess && whoAmIData) {
            dispatch(setUser(whoAmIData));
        }
    }, [isWhoAmIError, isWhoAmISuccess, whoAmIData, dispatch]);

    const router = createBrowserRouter(
        createRoutesFromElements(
            <>
                <Route
                    path="/"
                    element={
                        isAuth ? (
                            <Navigate
                                to="/dashboard"
                                replace
                            />
                        ) : (
                            <Navigate
                                to="/login"
                                replace
                            />
                        )
                    }
                />
                <Route
                    path="/login"
                    element={<Auth />}
                />
                <Route
                    path="/register"
                    element={<Register />}
                />
                <Route element={<PrivateRoute isAuth={isAuth} />}>
                    <Route
                        path={"/"}
                        element={<Layout />}
                    >
                        <Route
                            index
                            element={
                                <RedirectRoute
                                    route={"dashboard"}
                                    isAuth={isAuth}
                                />
                            }
                        />
                        <Route
                            path="/dashboard"
                            element={<Dashboard />}
                        />
                        <Route
                            path="/boards"
                            element={<Boards />}
                        />
                        <Route
                            path="/boards/new"
                            element={<BoardNew />}
                        />
                        <Route
                            path="/boards/:id"
                            element={<Board />}
                        />
                        <Route
                            path="/boards/:boardId/tasks/:taskId"
                            element={<Task />}
                        />
                    </Route>
                </Route>
            </>
        )
    );

    if (!isWhoAmIChecked) {
        return (
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "center",
                    flexDirection: "column",
                    alignItems: "center",
                    height: "100vh",
                }}
            >
                <Spinner />
            </Box>
        );
    }

    return <RouterProvider router={router} />;
};

export default App;
