// used to implement refetching statistics on page load

"use client";
import { createContext, useContext, useState } from "react";

export const RefreshContext = createContext(null);

export function RefreshProvider({ children }) {
    const [refetched, setRefetched] = useState(false);

    return (
        <RefreshContext.Provider value={{ refetched, setRefetched }}>
            {children}
        </RefreshContext.Provider>
    );
}

export const useRefresh = () => useContext(RefreshContext);
