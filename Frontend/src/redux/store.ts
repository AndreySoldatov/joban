import { configureStore } from '@reduxjs/toolkit';
import { authApi } from './api/auth.api';
import { setupListeners } from '@reduxjs/toolkit/query';
import { authSlice } from './slices/auth.slice';

export const store = configureStore({
    reducer: {
        [authApi.reducerPath]: authApi.reducer,
        authSlice: authSlice.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: false,
        }).concat(authApi.middleware),
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
