import React, { useState } from 'react';
import classes from './sidebar.module.sass';
import RouterLink from '../../utils/RouterLink';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';

const Sidebar: React.FC = () => {
    const [menu] = useState([
        {
            path: '/boards',
            text: 'Ваши доски',
            icon: <DashboardOutlinedIcon />,
        },
    ]);

    return (
        <aside className={classes.aside}>
            <div>
                <ul className={classes.menu}>
                    {menu.map((link, idx) => (
                        <li key={idx}>
                            <RouterLink to={link.path}>
                                <span>{link.icon}</span>
                                <span>{link.text}</span>
                            </RouterLink>
                        </li>
                    ))}
                </ul>
            </div>
        </aside>
    );
};

export default Sidebar;
