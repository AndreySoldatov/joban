import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import classes from './styles/Boards.module.sass';
import { Box, IconButton, Typography } from '@mui/material';
import { AddOutlined } from '@mui/icons-material';
import { useGetBoardsQuery } from '../../redux/api/boards.api';
import Spinner from '../../components/Spinner/Spinner';
import oops from '../../assets/images/oops.svg';

const Boards: React.FC = () => {
    const {
        data: boards,
        isLoading: isBoardsLoading,
        isSuccess: isBoardsSuccess,
        isError: isBoardsError,
    } = useGetBoardsQuery();
    const navigate = useNavigate();

    return (
        <div style={{ width: '100%' }}>
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                }}
            >
                <h1>Доски</h1>
                <IconButton onClick={() => navigate('/boards/new')}>
                    <AddOutlined />
                </IconButton>
            </div>
            {isBoardsLoading && (
                <Box
                    sx={{
                        display: 'flex',
                        justifyContent: 'center',
                        position: 'relative',
                    }}
                >
                    <Spinner />
                </Box>
            )}
            {isBoardsError && (
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                    }}
                >
                    <img src={oops} height={256} />
                    <Typography variant="h5" sx={{ mt: 5 }} color="primary">
                        Что-то пошло не так... Попробуйте позже
                    </Typography>
                </Box>
            )}
            {isBoardsSuccess && (
                <Box
                    sx={{
                        paddingTop: '18px',
                        display: 'flex',
                        gap: '18px',
                        flexWrap: 'wrap',
                    }}
                >
                    {boards.length > 0 ? (
                        boards.map((board) => (
                            <div className={classes.container} key={board.id}>
                                <Link
                                    className={classes.board_link}
                                    to={`/boards/${board.id}`}
                                >
                                    {board.title}
                                </Link>
                            </div>
                        ))
                    ) : (
                        <p>У вас нет активных досок</p>
                    )}
                </Box>
            )}
        </div>
    );
};

export default Boards;
