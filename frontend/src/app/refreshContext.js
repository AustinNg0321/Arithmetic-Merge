"use client";
import { createContext, useContext, useState } from "react";

// This context tells the browser when to refresh data by tracking global context
export const RefreshContext = createContext(null);

// Create a provider component to manage the state and provide it
export const RefreshProvider = ({ children }) => {
    const [refreshStatistics, setRefreshStatistics] = useState(false);

    return (
        <RefreshContext.Provider value={{ refreshStatistics, setRefreshStatistics }}>
            {children}
        </RefreshContext.Provider>
    );
};

export const useRefresh = () => useContext(RefreshContext);
