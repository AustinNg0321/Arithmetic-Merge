"use client";

import { useEffect } from "react";
import Link from "next/link";
import { SPACE } from "../../../utils/game";
import { useGame } from "./gameContext";
import "./gameGrid.css";

function parse(cell) {
    switch (cell) {
        case 1001:
        case "+":
            return "+";
        case 1002:
        case "-":
            return "-";
        case 1003:
        case "*":
            return "*";
        case 1004:
        case SPACE:
            return " ";
        default:
            return cell.toString();
    }
}

function Game({ curGame }) {
    return (
        <div className="container mb-5 text-center">
            {curGame.grid.map((row, r) => (
                <div key={r} className="row flex">
                    {row.map((cell, c) => (
                        <div key={c} className="cell flex items-center justify-center font-bold m-1
                        bg-blue-100 border border-gray-300 aspect-square size-1/12 lg:size-16
                        text-md lg:text-2xl rounded-sm lg:rounded-lg">
                            {parse(cell)}
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
}

function SoloHeader({ state }) {
    return (
        <header className="relative mb-6 w-full">
            <div className="absolute right-0 top-0">
                <Back />
            </div>
            <div className="flex flex-col">
                <div className="pr-24 text-left">
                    <h1 className="text-3xl font-bold text-gray-800">Solo Mode</h1>
                    <p className="mt-2 text-lg text-gray-500">Reach 67 before the board locks up.</p>
                </div>
                <p className="text-sm text-gray-500 mt-5 mb-5 md:hidden">
                    Best played on desktop with arrow keys.
                </p>
                <div className="mt-4 flex justify-start">
                    <StatusBadge state={state} />
                </div>
            </div>
        </header>
    );
}

function StatusBadge({ state }) {
    const styles = {
        "In Progress": "border border-blue-200 bg-blue-100 text-blue-700",
        Won: "border border-emerald-200 bg-emerald-100 text-emerald-700",
        Lost: "border border-red-200 bg-red-100 text-red-700",
    };

    const labels = {
        "In Progress": "In Progress",
        Won: "🎉 You Win!",
        Lost: "💀 Game Over",
    };

    return (
        <div className={`inline-flex items-center rounded-full px-4 py-2 text-sm font-semibold ${styles[state] ?? styles["In Progress"]}`}>
            {labels[state] ?? state}
        </div>
    );
}

function ControlsCard() {
    const controls = [
        { key: "↑", label: "Slide Up" },
        { key: "↓", label: "Slide Down" },
        { key: "←", label: "Slide Left" },
        { key: "→", label: "Slide Right" },
    ];

    return (
        <section className="mb-6 w-full rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
            <h2 className="mb-2 text-sm font-semibold text-gray-700">Controls</h2>
            <div className="grid grid-cols-2 gap-3">
                {controls.map((control) => (
                    <div key={control.key} className="flex items-center gap-2 text-sm text-gray-600">
                        <span className="rounded border border-gray-300 bg-gray-100 px-2 py-1 font-mono text-xs">
                            {control.key}
                        </span>
                        <span>{control.label}</span>
                    </div>
                ))}
            </div>
        </section>
    );
}

function GoalCard() {
    return (
        <section className="mb-6 w-full rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
            <div className="mb-3 rounded-lg bg-emerald-50 p-3 text-center">
                <p className="font-semibold text-emerald-700">🎯 Reach 67 to win</p>
            </div>
            <div className="mb-3 rounded-lg bg-red-50 p-3 text-center">
                <p className="font-semibold text-gray-600">No valid moves remain</p>
            </div>
            <div className="mb-3 rounded-lg bg-red-50 p-3 text-center">
                <p className="font-semibold text-gray-600">Tile exceeds 1000 or drops below -1000</p>
            </div>
        </section>
    );
}

function Back() {
    return (
        <div className="flex">
            <Link
                href="/"
                className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white
                transition-colors hover:bg-emerald-700">
                Back
            </Link>
        </div>
    );
}

export default function Solo() {
    const { game, move, restart, isRestarting } = useGame();

    useEffect(() => {
        function handleKeyDown(e) {
            switch (e.key) {
                case "ArrowUp":
                    e.preventDefault();
                    move("up");
                    break;
                case "ArrowDown":
                    e.preventDefault();
                    move("down");
                    break;
                case "ArrowLeft":
                    e.preventDefault();
                    move("left");
                    break;
                case "ArrowRight":
                    e.preventDefault();
                    move("right");
                    break;
                default:
                    break;
            }
        }

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [move]);

    if (!game) {
        return <p>Loading Game ...</p>;
    }

    return (
        <main className="mx-auto max-w-6xl px-6 py-10">
            <div className="flex flex-col gap-8 lg:justify-between">
                <SoloHeader state={game.state} />
            
                <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
                    <div className="flex w-full flex-col items-start">
                        <Game curGame={game} />
                        <button
                            className={`${isRestarting ? 'opacity-50 cursor-not-allowed' 
                                : 'cursor-pointer hover:bg-emerald-700'}
                            restart mb-4 pl-5 pr-5 pt-2.5 pb-2.5 text-lg 
                            rounded-md border bg-emerald-500 text-white`}
                            onClick={restart}
                            disabled={isRestarting}>
                            Restart
                        </button>
                    </div>
                    <div className="flex w-full max-w-sm flex-col">
                        <ControlsCard />
                        <GoalCard />
                    </div>
                </div>
            </div>
        </main>
    );
}
