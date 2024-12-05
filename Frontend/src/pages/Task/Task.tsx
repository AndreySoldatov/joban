import React, { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import {
    TextField,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Box,
    IconButton,
} from "@mui/material";
import { EditOutlined } from "@mui/icons-material";
import { marked } from "marked";
import html2md from "html-to-md";
import styles from "./styles/Task.module.sass";

marked.use({
    renderer: {
        link(token) {
            return `<a href="${token.href}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation()">${token.text}</a>`;
        },
    },
});

const Task: React.FC = () => {
    const defaultValues = {
        description: "",
        title: "",
    };

    const {
        control,
        handleSubmit,
        setValue,
        formState: { errors },
    } = useForm({ defaultValues });

    const [isOpenEditTitle, setIsOpenEditTitle] = useState<boolean>(false);
    const [isOpenEditDescription, setIsOpenEditDescription] =
        useState<boolean>(false);
    const [taskTitle, setTaskTitle] = useState<string>("Название таски");
    const [taskDescription, setTaskDescription] = useState<
        string | Promise<string>
    >("<p>Описание задачи</p>");
    const handleOpenEditTitle = () => setIsOpenEditTitle(true);
    const handleCloseEditTitle = () => setIsOpenEditTitle(false);

    const handleOpenEditDescription = async () => {
        const markdown = html2md(await taskDescription);
        setValue("description", markdown);
        setIsOpenEditDescription(true);
    };
    const handleCloseEditDescription = () => setIsOpenEditDescription(false);

    const onSubmitDescription = (data: any) => {
        const html = marked.parse(data.description, { breaks: true });
        setTaskDescription(html);
        handleCloseEditDescription();
    };

    return (
        <Box width={"40vw"}>
            <Box sx={{ display: "flex", alignItems: "center", gap: "18px" }}>
                <h1>{taskTitle}</h1>
                <IconButton
                    color="primary"
                    onClick={handleOpenEditTitle}
                >
                    <EditOutlined />
                </IconButton>
            </Box>
            <Box
                onClick={handleOpenEditDescription}
                className={styles.descriptionContainer}
                dangerouslySetInnerHTML={{ __html: taskDescription }}
            ></Box>

            <Dialog
                open={isOpenEditTitle}
                onClose={handleCloseEditTitle}
                fullWidth
                maxWidth={"sm"}
            >
                <DialogTitle>Редактирование названия</DialogTitle>
                <DialogContent>
                    <Controller
                        name="title"
                        control={control}
                        rules={{ required: "Название задачи обязательно" }}
                        defaultValue=""
                        render={({ field }) => (
                            <TextField
                                {...field}
                                autoFocus
                                margin="dense"
                                label="Название задачи"
                                type="text"
                                fullWidth
                                variant="outlined"
                                error={!!errors.title}
                                helperText={errors.title?.message}
                            />
                        )}
                    />
                </DialogContent>
                <DialogActions>
                    <Button
                        color="error"
                        onClick={handleCloseEditTitle}
                    >
                        Отмена
                    </Button>
                    <Button
                        color="primary"
                        onClick={() => {
                            setTaskTitle(defaultValues.title);
                            handleCloseEditTitle();
                        }}
                    >
                        Сохранить
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Диалог для редактирования описания */}
            <Dialog
                open={isOpenEditDescription}
                onClose={handleCloseEditDescription}
                fullWidth
                maxWidth={"lg"}
            >
                <DialogTitle>Редактирование описания</DialogTitle>
                <form onSubmit={handleSubmit(onSubmitDescription)}>
                    <DialogContent>
                        <Controller
                            name="description"
                            control={control}
                            defaultValue=""
                            render={({ field }) => (
                                <TextField
                                    {...field}
                                    autoFocus
                                    margin="dense"
                                    label="Описание задачи"
                                    type="text"
                                    fullWidth
                                    multiline
                                    rows={10}
                                    variant="outlined"
                                />
                            )}
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button
                            color="error"
                            onClick={handleCloseEditDescription}
                        >
                            Отмена
                        </Button>
                        <Button
                            type="submit"
                            color="primary"
                        >
                            Сохранить
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
};

export default Task;
