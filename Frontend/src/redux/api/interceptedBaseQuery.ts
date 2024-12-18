import {
    fetchBaseQuery,
    BaseQueryFn,
    FetchArgs,
    FetchBaseQueryError,
} from "@reduxjs/toolkit/query";

const customBaseQuery = fetchBaseQuery({
    baseUrl: "https://joban.ddns.net",
    credentials: "include",
});

export const interceptedBaseQuery: BaseQueryFn<
    string | FetchArgs,
    unknown,
    FetchBaseQueryError
> = async (args, api, extraOptions) => {
    const response = await customBaseQuery(args, api, extraOptions);

    if (
        response.error &&
        response.error.status === 401 &&
        window.location.pathname !== "/login" &&
        window.location.pathname !== "/register"
    ) {
        window.location.href = "/login";
        return { error: { status: 401, data: "Unauthorized" } };
    }

    return response;
};
