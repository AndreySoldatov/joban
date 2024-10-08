import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
    displayName: string | null;
    isAuth: boolean;
    isWhoAmIChecked: boolean;
}

const initialState: AuthState = {
    displayName: null,
    isAuth: false,
    isWhoAmIChecked: false,
};

export const authSlice = createSlice({
    name: 'authSlice',
    initialState,
    reducers: {
        setUser: (
            state,
            action: PayloadAction<{
                displayName: string;
            }>
        ) => {
            state.displayName = action.payload.displayName;
            state.isAuth = true;
            state.isWhoAmIChecked = true;
        },
        resetUser: (state) => {
            state.displayName = null;
            state.isAuth = false;
            state.isWhoAmIChecked = true;
        },
    },
});

export const { setUser, resetUser } = authSlice.actions;
