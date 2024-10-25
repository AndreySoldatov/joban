import React from 'react';
import { Card, CardContent, Typography, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import styles from '../styles/Task.module.sass';

interface TaskProps {
    task: { id: string; title: string };
    onDelete: (taskId: string) => void; // Функция для удаления задачи
}

const Task: React.FC<TaskProps> = ({ task, onDelete }) => {
    return (
        <Card className={styles.task} variant="outlined">
            <CardContent className={styles.task__body}>
                <Typography>{task.title}</Typography>
                <IconButton
                    className={styles.deleteButton}
                    onClick={() => onDelete(task.id)}
                    size="small"
                    color="error"
                    aria-label="Удалить задачу"
                >
                    <DeleteIcon />
                </IconButton>
            </CardContent>
        </Card>
    );
};

export default Task;
