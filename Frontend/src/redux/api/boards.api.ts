import { createApi } from '@reduxjs/toolkit/query/react';
import { interceptedBaseQuery } from './interceptedBaseQuery';

export const boardsApi = createApi({
    reducerPath: 'boardsApi',
    baseQuery: interceptedBaseQuery,
    endpoints: (builder) => ({
        createBoard: builder.mutation({
            query: (body) => ({
                url: '/boards/new',
                method: 'POST',
                body: body,
            }),
        }),
        getBoards: builder.query<
            Array<{ id: number; title: string }> | undefined,
            void
        >({
            query: () => '/boards',
        }),
    }),
});

export const { useCreateBoardMutation, useGetBoardsQuery } = boardsApi;
