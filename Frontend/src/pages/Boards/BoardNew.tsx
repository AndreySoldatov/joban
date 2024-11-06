import { Button, IconButton, TextField, Typography } from '@mui/material';
import React, { useEffect } from 'react';
import { SubmitHandler, useFieldArray, useForm } from 'react-hook-form';
import style from './styles/BoardNew.module.sass';
import {
    ArrowDownwardOutlined,
    ArrowUpwardOutlined,
    DeleteOutlineOutlined,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useCreateBoardMutation } from '../../redux/api/boards.api';
import { toast, ToastContainer } from 'react-toastify';

interface ColumnData {
    title: string;
}

interface BoardData {
    title: string;
    columns: Array<ColumnData>;
}

const BoardNew: React.FC = () => {
    const navigate = useNavigate();
    const notifyError = (message?: string) =>
        toast.error(message || 'Что-то пошло не так...');

    const [
        createBoard,
        {
            data: createBoardData,
            isSuccess: isCreateBoardSuccess,
            isError: isCreateBoardError,
            isLoading: isCreateBoardLoading,
        },
    ] = useCreateBoardMutation();

    const {
        register,
        handleSubmit,
        control,
        formState: { errors },
    } = useForm<BoardData>();

    const { fields, replace, append, remove, move } = useFieldArray({
        control,
        name: 'columns',
    });

    useEffect(() => {
        replace([{ title: '' }, { title: '' }]);
    }, []);

    useEffect(() => {
        if (isCreateBoardSuccess) navigate(`/boards/${createBoardData.id}`);
    }, [isCreateBoardSuccess]);

    useEffect(() => {
        if (isCreateBoardError) notifyError();
    }, [isCreateBoardError]);

    const onSubmit: SubmitHandler<BoardData> = async (data) => {
        const result = {
            title: data.title,
            columns: data.columns.map((column, index) => ({
                title: column.title,
                orderNumber: index,
            })),
        };

        await createBoard(result);
    };

    return (
        <>
            <ToastContainer
                position="top-center"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="colored"
            />

            <div style={{ width: '100%' }}>
                <h1>Создать доску</h1>
                <form onSubmit={handleSubmit(onSubmit)} className={style.form}>
                    <TextField
                        sx={{ width: '600px' }}
                        {...register('title', {
                            required: 'Введите название',
                        })}
                        label="Название доски"
                        id="title"
                        variant="outlined"
                        type="text"
                        error={!!errors.title}
                        helperText={
                            errors.title?.message &&
                            typeof errors.title?.message === 'string' &&
                            errors.title?.message
                        }
                    />
                    <div>
                        <Typography variant="h6">Колонки</Typography>
                        <ul className={style.input_list}>
                            {fields.map((item, index) => (
                                <li
                                    key={item.id}
                                    className={style.input_list__item}
                                >
                                    <TextField
                                        sx={{ width: '600px' }}
                                        {...register(`columns.${index}.title`, {
                                            required: 'Введите название',
                                        })}
                                        label="Название колонки"
                                        key={item.id}
                                        type="text"
                                        error={!!errors.columns?.[index]}
                                        helperText={
                                            errors.columns?.[index]?.title
                                                ?.message
                                        }
                                    />

                                    <div className={style.button_container}>
                                        <IconButton
                                            color="primary"
                                            onClick={() =>
                                                move(index, index - 1)
                                            }
                                            disabled={index === 0}
                                        >
                                            <ArrowUpwardOutlined />
                                        </IconButton>

                                        <IconButton
                                            color="primary"
                                            onClick={() =>
                                                move(index, index + 1)
                                            }
                                            disabled={
                                                index === fields.length - 1
                                            }
                                        >
                                            <ArrowDownwardOutlined />
                                        </IconButton>

                                        <IconButton
                                            color="error"
                                            onClick={() => remove(index)}
                                            disabled={fields.length <= 2}
                                        >
                                            <DeleteOutlineOutlined />
                                        </IconButton>
                                    </div>
                                </li>
                            ))}
                        </ul>
                        {fields.length < 5 && (
                            <Button
                                variant="outlined"
                                onClick={() => append({ title: '' })}
                            >
                                Добавить колонку
                            </Button>
                        )}
                    </div>
                    <div className={style.button_group}>
                        <Button
                            variant="outlined"
                            color="primary"
                            type="submit"
                            disabled={isCreateBoardLoading}
                        >
                            Сохранить
                        </Button>
                        <Button
                            variant="outlined"
                            color="error"
                            onClick={() => navigate('/boards')}
                        >
                            Отмена
                        </Button>
                    </div>
                </form>
            </div>
        </>
    );
};

export default BoardNew;
