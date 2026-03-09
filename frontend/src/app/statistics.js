"use client";

import { useEffect, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { useRefresh } from "./refreshContext";
import "./globals.css";

const STATISTICS_KEY = "statistics";
const STATISTICS_UPDATED_EVENT = "statistics-updated";
const STATISTICS_URL = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/statistics`;
const DEFAULT_STATISTICS = {
    user_id: "-",
    wins: "-",
    losses: "-",
    abandoned: "-",
};

function Statistics({ data }) {
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

function readStatisticsFromStorage() {
    const rawValue = window.sessionStorage.getItem(STATISTICS_KEY);
    if (!rawValue) {
        return null;
    }

    const parsedValue = JSON.parse(rawValue);
    if (
        !parsedValue ||
        typeof parsedValue.user_id !== "string" ||
        typeof parsedValue.wins !== "number" ||
        typeof parsedValue.losses !== "number" ||
        typeof parsedValue.abandoned !== "number"
    ) {
        throw new Error("Invalid cached statistics payload");
    }

    return parsedValue;
}

function writeStatisticsToStorage(statistics) {
    window.sessionStorage.setItem(STATISTICS_KEY, JSON.stringify(statistics));
}

function broadcastStatistics(statistics) {
    window.dispatchEvent(new CustomEvent(STATISTICS_UPDATED_EVENT, { detail: statistics }));
}

async function fetchStatistics() {
    const response = await fetch(STATISTICS_URL, {
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
    }

    return response.json();
}

function StatisticsContainerInner() {
    const {refetched, setRefetched} = useRefresh();
    const [error, setError] = useState(null);
    const [statistics, setStatistics] = useState(() => {
        if (typeof window === "undefined") {
            return null;
        }

        try {
            return readStatisticsFromStorage();
        } catch (error) {
            console.error("Failed to read cached statistics", error);
            return null;
        }
    });

    useEffect(() => {
        let isActive = true;
        
        function handleStatisticsUpdated(event) {
            setStatistics(event.detail);
            setError(null);
        }

        if (statistics && refetched) {
            window.addEventListener(STATISTICS_UPDATED_EVENT, handleStatisticsUpdated);
            return () => {
                isActive = false;
                window.removeEventListener(STATISTICS_UPDATED_EVENT, handleStatisticsUpdated);
            };
        }

        // add fallback to sessionStorage if refetching fails
        fetchStatistics()
            .then((data) => {
                setRefetched(true);
                if (!isActive) {
                    return;
                }
                try {
                    writeStatisticsToStorage(data);
                } catch (writeError) {
                    console.error("Failed to cache fetched statistics", writeError);
                }
                broadcastStatistics(data);
                setStatistics(data);
                setError(null);
            })
            .catch((loadError) => {
                if (!isActive) {
                    return;
                }
                setError(loadError);
            });

        window.addEventListener(STATISTICS_UPDATED_EVENT, handleStatisticsUpdated);

        return () => {
            isActive = false;
            window.removeEventListener(STATISTICS_UPDATED_EVENT, handleStatisticsUpdated);
        };
    }, [statistics, refetched, setRefetched]);

    if (error) {
        throw error;
    }

    if (!statistics) {
        return <Statistics data={DEFAULT_STATISTICS} />;
    }

    return <Statistics data={statistics} />;
}

export default function StatisticsContainer() {
    return (
        <ErrorBoundary fallback={<p className="mb-5">Failed to fetch data</p>}>
            <StatisticsContainerInner />
        </ErrorBoundary>
    );
}
