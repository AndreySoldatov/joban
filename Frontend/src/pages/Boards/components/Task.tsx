import React, { useState } from 'react';
import {
    Card,
    CardContent,
    Typography,
    IconButton,
    Dialog,
    DialogTitle,
    DialogActions,
    Button,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import styles from '../styles/Task.module.sass';

interface TaskProps {
    task: { id: string; title: string };
    onDelete: (taskId: string) => void; // Функция для удаления задачи
}

const Task: React.FC<TaskProps> = ({ task, onDelete }) => {
    const [isOpenDeleteDialog, setIsOpenDeleteDialog] = useState(false);

    const handleClickDelete = () => {
        setIsOpenDeleteDialog(true);
    };

    const handleCloseDialog = () => {
        setIsOpenDeleteDialog(false);
    };

    return (
        <>
            <Card className={styles.task} variant="outlined">
                <CardContent className={styles.task__body}>
                    <Typography>{task.title}</Typography>
                    <IconButton
                        className={styles.deleteButton}
                        onClick={handleClickDelete}
                        size="small"
                        color="error"
                        aria-label="Удалить задачу"
                    >
                        <DeleteIcon />
                    </IconButton>
                </CardContent>
            </Card>

            <Dialog
                open={isOpenDeleteDialog}
                onClose={handleCloseDialog}
                fullWidth
                maxWidth={'sm'}
            >
                <DialogTitle>Вы хотите удалить задачу?</DialogTitle>
                <DialogActions>
                    <Button onClick={handleCloseDialog} color="primary">
                        Отмена
                    </Button>
                    <Button
                        onClick={() => onDelete(task.id)}
                        color="error"
                        type="submit"
                        variant="contained"
                    >
                        Удалить
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default Task;
