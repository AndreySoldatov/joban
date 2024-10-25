import React, { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header/Header';
import Sidebar from './Sidebar/Sidebar';

const Layout: React.FC = () => {
    const location = useLocation();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [location.pathname]);

    return (
        <>
            <Header />
            <main className="main">
                <div className="container" style={{ padding: 0 }}>
                    <div className="wrapper" style={{ padding: 0 }}>
                        <Sidebar />
                        <article className="content">
                            <Outlet />
                        </article>
                    </div>
                </div>
            </main>
        </>
    );
};

export default Layout;
