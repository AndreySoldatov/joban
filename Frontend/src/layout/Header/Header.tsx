import React, { useEffect } from 'react';
import { useLogoutUserMutation } from '../../redux/api/auth.api';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { resetUser } from '../../redux/slices/auth.slice';
import { Box, IconButton, Typography } from '@mui/material';
import classes from './header.module.sass';
import Icon from '../../components/Icon/Icon';
import { Logout } from '@mui/icons-material';
import { RootState } from '../../redux/store';

const Header: React.FC = () => {
    const [logoutUser, { isSuccess: isLogoutSuccess }] =
        useLogoutUserMutation();

    const { displayName } = useSelector((state: RootState) => state.authSlice);
    const dispatch = useDispatch();
    const navigate = useNavigate();

    useEffect(() => {
        if (isLogoutSuccess) {
            dispatch(resetUser());
            navigate('/login');
        }
    }, [isLogoutSuccess]);

    const handleLogoutClick = async () => {
        await logoutUser();
    };

    return (
        <Box className={classes.header}>
            <div className="container">
                <Box
                    sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                    }}
                >
                    <Box
                        className={classes.header__logo}
                        onClick={() => navigate('/dashboard')}
                    >
                        <Icon name={'logo'} size={48} />
                    </Box>
                    <Box
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '18px',
                        }}
                    >
                        <Typography>{displayName}</Typography>
                        <IconButton onClick={handleLogoutClick}>
                            <Logout />
                        </IconButton>
                    </Box>
                </Box>
            </div>
        </Box>
    );
};

export default Header;
