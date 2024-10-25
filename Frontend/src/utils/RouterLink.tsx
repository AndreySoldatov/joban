import React from 'react';
import { Link, useMatch, useResolvedPath } from 'react-router-dom';

interface Props {
    children: React.ReactNode;
    to: string;
}

const RouterLink: React.FC<Props> = ({ children, to, ...props }) => {
    let resolved = useResolvedPath(to);
    let match = useMatch({ path: resolved.pathname, end: false });

    return (
        <Link className={match ? 'active' : ''} to={to} {...props}>
            {children}
        </Link>
    );
};

export default RouterLink;
