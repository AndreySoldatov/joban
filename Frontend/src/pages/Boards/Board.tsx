import React, { useState } from 'react';
import {
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Button,
    TextField,
    Grid2,
} from '@mui/material';
import Column from './components/Column';
import { useForm, Controller } from 'react-hook-form';

interface Task {
    id: string;
    title: string;
}

interface ColumnData {
    id: string;
    title: string;
    tasks: Task[];
}

const Board: React.FC = () => {
    const [columns, setColumns] = useState<ColumnData[]>([
        {
            id: 'not-started',
            title: 'Not Started',
            tasks: [],
        },
        {
            id: 'development',
            title: 'Development',
            tasks: [],
        },
        { id: 'done', title: 'Done', tasks: [] },
    ]);
    const [openDialog, setOpenDialog] = useState(false);
    const [targetColumnId, setTargetColumnId] = useState<string | null>(null);

    const {
        control,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<{ title: string }>({
        mode: 'onChange',
    });

    const handleOpenDialog = (columnId: string) => {
        setTargetColumnId(columnId);
        setOpenDialog(true);
        setTimeout(() => {
            const input = document.querySelector(
                'input[name="title"]'
            ) as HTMLInputElement;
            if (input) input.focus();
        }, 0);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        reset();
    };

    const onSubmit = handleSubmit(({ title }) => {
        if (targetColumnId) {
            setColumns((prevColumns) =>
                prevColumns.map((col) =>
                    col.id === targetColumnId
                        ? {
                              ...col,
                              tasks: [
                                  ...col.tasks,
                                  {
                                      id: new Date().getTime().toString(),
                                      title,
                                  },
                              ],
                          }
                        : col
                )
            );
        }
        handleCloseDialog();
    });

    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            onSubmit();
        }
    };

    return (
        <>
            <Grid2 container width={'100%'} spacing={2}>
                {columns.map((column) => (
                    <Grid2 size={4} key={column.id}>
                        <Column
                            column={column}
                            setColumns={setColumns}
                            onAddTaskClick={handleOpenDialog}
                        />
                    </Grid2>
                ))}
            </Grid2>

            <Dialog
                open={openDialog}
                onClose={handleCloseDialog}
                fullWidth
                maxWidth={'sm'}
            >
                <DialogTitle>Добавление новой задачи</DialogTitle>
                <DialogContent>
                    <Controller
                        name="title"
                        control={control}
                        rules={{ required: 'Название задачи обязательно' }}
                        defaultValue=""
                        render={({ field }) => (
                            <TextField
                                {...field}
                                autoFocus
                                margin="dense"
                                label="Название задачи"
                                required
                                type="text"
                                fullWidth
                                variant="outlined"
                                error={!!errors.title}
                                helperText={errors.title?.message}
                                onKeyDown={handleKeyDown}
                            />
                        )}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog} color="error">
                        Отмена
                    </Button>
                    <Button
                        onClick={onSubmit}
                        color="primary"
                        type="submit"
                        variant="contained"
                    >
                        Добавить
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default Board;
