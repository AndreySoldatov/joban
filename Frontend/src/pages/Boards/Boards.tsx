import React from 'react';
import { Link } from 'react-router-dom';
import classes from './styles/Boards.module.sass';
import { Box } from '@mui/material';

const Boards: React.FC = () => {
    const boards = [{ id: 1, title: 'Досочка' }];

    return (
        <div>
            <h1>BOARDS</h1>
            <Box
                sx={{
                    paddingTop: '18px',
                    display: 'flex',
                    gap: '18px',
                    flexWrap: 'wrap',
                }}
            >
                {boards.map((board) => (
                    <div className={classes.container}>
                        <Link
                            key={board.id}
                            className={classes.board_link}
                            to={`/boards/${board.id}`}
                        >
                            {board.title}
                        </Link>
                    </div>
                ))}
            </Box>
        </div>
    );
};

export default Boards;
