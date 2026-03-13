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
    const metrics = [
        { label: "Wins", value: data.wins },
        { label: "Losses", value: data.losses },
        { label: "Abandoned", value: data.abandoned },
    ];

    return (
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {metrics.map((metric) => (
                <div
                    key={metric.label}
                    className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
                >
                    <p className="text-3xl font-bold text-emerald-600">{metric.value}</p>
                    <p className="mt-2 text-sm text-gray-500">{metric.label}</p>
                </div>
            ))}
        </section>
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
        <ErrorBoundary fallback={<p className="text-gray-500">Failed to fetch data</p>}>
            <StatisticsContainerInner />
        </ErrorBoundary>
    );
}
