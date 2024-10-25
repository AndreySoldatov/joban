import React from 'react';
import { ReactSortable } from 'react-sortablejs';
import { Card, CardHeader, IconButton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import Task from './Task';
import styles from '../styles/Column.module.sass';

interface Task {
    id: string;
    title: string;
}

interface ColumnData {
    id: string;
    title: string;
    tasks: Task[];
}

interface ColumnProps {
    column: ColumnData;
    setColumns: React.Dispatch<React.SetStateAction<ColumnData[]>>;
    onAddTaskClick: (columnId: string) => void;
}

const Column: React.FC<ColumnProps> = ({
    column,
    setColumns,
    onAddTaskClick,
}) => {
    const handleDeleteTask = (taskId: string) => {
        setColumns((prevColumns) =>
            prevColumns.map((col) =>
                col.id === column.id
                    ? {
                          ...col,
                          tasks: col.tasks.filter((task) => task.id !== taskId),
                      }
                    : col
            )
        );
    };

    return (
        <Card className={styles.column}>
            <CardHeader
                title={column.title}
                action={
                    <IconButton onClick={() => onAddTaskClick(column.id)}>
                        <AddIcon />
                    </IconButton>
                }
            />
            <ReactSortable
                tag="ul"
                list={column.tasks}
                setList={(newList) => {
                    setColumns((prevColumns) =>
                        prevColumns.map((col) =>
                            col.id === column.id
                                ? { ...col, tasks: newList }
                                : col
                        )
                    );
                }}
                group={{ name: 'list', pull: true, put: true }}
                handle="li"
                animation={200}
                delayOnTouchOnly={true}
            >
                {column.tasks.map((task) => (
                    <li key={task.id}>
                        <Task onDelete={handleDeleteTask} task={task} />
                    </li>
                ))}
            </ReactSortable>
        </Card>
    );
};

export default Column;
