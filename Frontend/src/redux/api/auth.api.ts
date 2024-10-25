import { createApi } from '@reduxjs/toolkit/query/react';
import { interceptedBaseQuery } from './interceptedBaseQuery';

export const authApi = createApi({
    reducerPath: 'authApi',
    baseQuery: interceptedBaseQuery,
    endpoints: (builder) => ({
        registerUser: builder.mutation({
            query: (credentials) => ({
                url: '/auth/register',
                method: 'POST',
                body: credentials,
            }),
        }),
        loginUser: builder.mutation({
            query: (credentials) => ({
                url: '/auth/login',
                method: 'POST',
                body: credentials,
            }),
        }),
        logoutUser: builder.mutation<void, void>({
            query: () => ({
                url: '/auth/logout',
                method: 'POST',
            }),
        }),
        whoAmI: builder.query({
            query: () => '/auth/whoami',
        }),
    }),
});

export const {
    useLoginUserMutation,
    useLogoutUserMutation,
    useWhoAmIQuery,
    useRegisterUserMutation,
} = authApi;
