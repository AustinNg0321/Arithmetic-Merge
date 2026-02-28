"use client";
import { use, Suspense, useEffect, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";
import "./globals.css";
import { useRefresh } from "./refreshContext";

function Statistics({ messagePromise }) {
    const data = use(messagePromise);
    return (
        <div className="mb-5">
            <ul>
                <li>UserID: {data.user_id}</li>
                <li>Wins: {data.wins}</li>
                <li>Losses: {data.losses}</li>
                <li>Abandoned Games: {data.abandoned}</li>
            </ul>
        </div>
    );
}

// change the link in prod
function fetchStatistics() {
    return fetch("http://localhost:5000/api/statistics", {
        credentials: "include",
    }).then(res => {
        if (!res.ok) {
            throw new Error(`HTTP error: ${res.status}`);
        }
        return res.json();
    });
}

// should be refetching every time the statistics change
// refreshStatistics is set to true whenever the statistics change, false immediately after refresh
export default function StatisticsContainer() {
    const {refreshStatistics, setRefreshStatistics} = useRefresh();
    const [messagePromise, setMessagePromise] = useState(() => fetchStatistics());
    
    useEffect(() => {
        if (refreshStatistics) {
            setMessagePromise(fetchStatistics());
            setRefreshStatistics(false);
        }
    }, [refreshStatistics]);
    
    return (
        <ErrorBoundary fallback={<p className="mb-5">Failed to fetch data</p>}>
            <Suspense fallback={<p className="mb-5">Loading ...</p>}>
                <Statistics messagePromise={messagePromise} />
            </Suspense>
        </ErrorBoundary>
    );
}
