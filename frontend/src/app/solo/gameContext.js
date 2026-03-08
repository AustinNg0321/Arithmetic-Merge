"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import {
    ADDITION,
    Game as ArithmeticGame,
    SPACE,
    SUBTRACTION,
    constructGrid,
} from "../../../utils/game";

const NUM_ROWS = 6;
const NUM_COLS = 7;
const INCLUDED_OPERATIONS = [ADDITION, SUBTRACTION];
const OPERATOR_SPAWN_RATE = 0.67;
const INCLUDED_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
const GENERATED_TILES_PER_TURN = 2;
const VALID_DIRECTIONS = new Set(["up", "down", "left", "right"]);
const VERIFY_GAME_URL = "http://localhost:5000/api/verify";
const RESTART_GAME_URL = "http://localhost:5000/api/restart";
const STORAGE_KEY = "solo-game-state";
const STATISTICS_KEY = "statistics";
const STATISTICS_UPDATED_EVENT = "statistics-updated";

export const GameContext = createContext(null);

function makeSeed() {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
        return crypto.randomUUID();
    }

    return `seed-${Date.now()}-${Math.random()}`;
}

function createGame(seed = makeSeed()) {
    const game = new ArithmeticGame(
        constructGrid(NUM_ROWS, NUM_COLS, SPACE),
        NUM_ROWS,
        NUM_COLS,
        INCLUDED_OPERATIONS,
        OPERATOR_SPAWN_RATE,
        INCLUDED_DIGITS,
        GENERATED_TILES_PER_TURN,
        seed,
    );

    game.generateTiles();
    return game;
}

function createSnapshot(game) {
    return {
        grid: game.getGame().map((row) => [...row]),
        state: game.getState(),
        seed: game.getSeed(),
        validMoves: game.getValidMoves(),
    };
}

function createVerificationSnapshot(game, moveList) {
    return {
        seed: game.getSeed(),
        moves: moveList,
    };
}

function applyMove(game, dir) {
    switch (dir) {
        case "up":
            game.slideUp();
            break;
        case "down":
            game.slideDown();
            break;
        case "left":
            game.slideLeft();
            break;
        case "right":
            game.slideRight();
            break;
        default:
            break;
    }
}

function restoreStoredGame() {
    if (typeof window === "undefined") {
        return null;
    }

    try {
        const rawValue = window.localStorage.getItem(STORAGE_KEY);
        if (!rawValue) {
            return null;
        }

        const parsedValue = JSON.parse(rawValue);
        if (
            !parsedValue ||
            typeof parsedValue.seed !== "string" ||
            !Array.isArray(parsedValue.moveList)
        ) {
            window.localStorage.removeItem(STORAGE_KEY);
            return null;
        }

        const restoredGame = createGame(parsedValue.seed);

        for (const move of parsedValue.moveList) {
            if (!VALID_DIRECTIONS.has(move)) {
                throw new Error(`Invalid move in saved game: ${move}`);
            }

            const validMoves = restoredGame.getValidMoves();
            if (!validMoves.includes(move) || restoredGame.getState() !== "In Progress") {
                throw new Error(`Saved game replay diverged at move: ${move}`);
            }

            applyMove(restoredGame, move);
            restoredGame.generateTiles();
        }

        return {
            game: restoredGame,
            moveList: parsedValue.moveList,
        };
    } catch (error) {
        console.error("Failed to restore solo game from localStorage", error);
        try {
            window.localStorage.removeItem(STORAGE_KEY);
        } catch (removeError) {
            console.error("Failed to clear corrupted solo game from localStorage", removeError);
        }
        return null;
    }
}

async function fetchStatistics() {
    const response = await fetch("http://localhost:5000/api/statistics", {
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch statistics with status ${response.status}`);
    }

    return response.json();
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

function syncStatistics(statistics) {
    writeStatisticsToStorage(statistics);
    broadcastStatistics(statistics);
}

async function updateStatisticsFromOutcome(outcome) {
    try {
        const currentStatistics = readStatisticsFromStorage();
        if (!currentStatistics) {
            throw new Error("No cached statistics available");
        }

        const nextStatistics = {
            ...currentStatistics,
            wins: currentStatistics.wins + (outcome === "Won" ? 1 : 0),
            losses: currentStatistics.losses + (outcome === "Lost" ? 1 : 0),
            abandoned: currentStatistics.abandoned + (outcome === "In Progress" ? 1 : 0),
        };

        syncStatistics(nextStatistics);
        return;
    } catch (error) {
        console.error("Failed to update cached statistics", error);
    }

    const fetchedStatistics = await fetchStatistics();

    try {
        syncStatistics(fetchedStatistics);
    } catch (error) {
        console.error("Failed to cache fetched statistics after update fallback", error);
        broadcastStatistics(fetchedStatistics);
    }
}


export function GameProvider({ children }) {
    const gameRef = useRef(null);
    const moveListRef = useRef([]);
    const inFlightVerificationKeysRef = useRef(new Set());
    const verifiedKeysRef = useRef(new Set());
    const [game, setGame] = useState(null);
    const [moveList, setMoveList] = useState([]);
    const [isRestarting, setIsRestarting] = useState(false);

    const verifyGame = useCallback(async (targetGame = gameRef.current) => {
        if (!targetGame) {
            return false;
        }

        const verificationSnapshot = createVerificationSnapshot(targetGame, moveListRef.current);
        const verificationKey = JSON.stringify(verificationSnapshot);

        if (verifiedKeysRef.current.has(verificationKey)) {
            return true;
        }

        if (inFlightVerificationKeysRef.current.has(verificationKey)) {
            return false;
        }

        inFlightVerificationKeysRef.current.add(verificationKey);

        try {
            const response = await fetch(VERIFY_GAME_URL, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(verificationSnapshot),
            });

            if (!response.ok) {
                throw new Error(`Verification failed with status ${response.status}`);
            }

            verifiedKeysRef.current.add(verificationKey);
            await updateStatisticsFromOutcome(targetGame.getState());
            return true;
        } catch (error) {
            console.error("Failed to verify solo game", error);
            return false;
        } finally {
            inFlightVerificationKeysRef.current.delete(verificationKey);
        }
    }, []);

    const abandonGame = useCallback(async (targetGame = gameRef.current) => {
        if (!targetGame) {
            return false;
        }

        try {
            const response = await fetch(RESTART_GAME_URL, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(
                    createVerificationSnapshot(targetGame, moveListRef.current),
                ),
            });

            if (!response.ok) {
                throw new Error(`Abandon request failed with status ${response.status}`);
            }

            await updateStatisticsFromOutcome("In Progress");
            return true;
        } catch (error) {
            console.error("Failed to abandon solo game", error);
            return false;
        }
    }, []);

    const commitGame = (nextGame, nextMoveList) => {
        gameRef.current = nextGame;
        moveListRef.current = nextMoveList;
        setMoveList(nextMoveList);
        setGame(createSnapshot(nextGame));
    };

    const move = (dir) => {
        const curGame = gameRef.current;
        if (!curGame || !VALID_DIRECTIONS.has(dir) || curGame.getState() !== "In Progress") {
            return;
        }

        const validMoves = curGame.getValidMoves();
        if (!validMoves.includes(dir)) {
            return;
        }

        applyMove(curGame, dir);
        curGame.generateTiles();

        const nextMoveList = [...moveListRef.current, dir];
        moveListRef.current = nextMoveList;
        setMoveList(nextMoveList);
        setGame(createSnapshot(curGame));
    };

    const restart = useCallback(async () => {
        setIsRestarting(true);
        setTimeout(() => setIsRestarting(false), 10000);

        let canRestart = true;
        const curGame = gameRef.current;
        if (curGame) {
            if (curGame.getState() === "In Progress") {
                canRestart = await abandonGame(curGame);
            } else {
                canRestart = await verifyGame(curGame);
            }
        }

        if (!canRestart) {
            return;
        }

        const nextGame = createGame();
        commitGame(nextGame, []);
    }, [abandonGame, verifyGame]);

    useEffect(() => {
        const timeoutId = window.setTimeout(() => {
            const restoredState = restoreStoredGame();
            if (restoredState) {
                commitGame(restoredState.game, restoredState.moveList);
                return;
            }

            commitGame(createGame(), []);
        }, 0);

        return () => window.clearTimeout(timeoutId);
    }, []);

    useEffect(() => {
        if (!game || typeof window === "undefined") {
            return;
        }

        try {
            window.localStorage.setItem(
                STORAGE_KEY,
                JSON.stringify({
                    seed: game.seed,
                    moveList,
                }),
            );
        } catch (error) {
            console.error("Failed to save solo game to localStorage", error);
        }
    }, [game, moveList]);

    useEffect(() => {
        if (!game || (game.state !== "Won" && game.state !== "Lost")) {
            return;
        }

        setIsRestarting(true);
        setTimeout(() => setIsRestarting(false), 10000);

        try {
            window.localStorage.removeItem(STORAGE_KEY);
        } catch (error) {
            console.error("Failed to clear finished solo game from localStorage", error);
        }

        void verifyGame(gameRef.current);
        
        const timeoutId = window.setTimeout(() => restart(), 2000);
        return () => window.clearTimeout(timeoutId);
    }, [game, restart, verifyGame]);

    return (
        <GameContext.Provider value={{ game, gameRef, moveList, move, restart, isRestarting, setIsRestarting }}>
            {children}
        </GameContext.Provider>
    );
}

export const useGame = () => useContext(GameContext);
