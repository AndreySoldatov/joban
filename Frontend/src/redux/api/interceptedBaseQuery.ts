import {
    fetchBaseQuery,
    BaseQueryFn,
    FetchArgs,
    FetchBaseQueryError,
} from '@reduxjs/toolkit/query';

const customBaseQuery = fetchBaseQuery({
    baseUrl: 'http://194.58.126.172:8000',
});

export const interceptedBaseQuery: BaseQueryFn<
    string | FetchArgs,
    unknown,
    FetchBaseQueryError
> = async (args, api, extraOptions) => {
    const response = await customBaseQuery(args, api, extraOptions);

    if (response.error && response.error.status === 401) {
        window.location.href = '/';
        return { error: { status: 401, data: 'Unauthorized' } };
    }

    return response;
};
