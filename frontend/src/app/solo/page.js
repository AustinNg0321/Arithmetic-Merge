"use client";

import { useEffect } from "react";
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
        <>
            <Game curGame={game} />
            <p className="mb-4 text-lg">{game.state}</p>
            <button
                className={`${isRestarting ? 'opacity-50 cursor-not-allowed' 
                    : 'cursor-pointer hover:bg-emerald-700'}
                restart pl-5 pr-5 pt-2.5 pb-2.5 text-lg 
                rounded-md border bg-emerald-500 text-white`}
                // "restart pl-5 pr-5 pt-2.5 pb-2.5 text-lg rounded-md border
                // bg-emerald-500 text-white cursor-pointer hover:bg-emerald-700"
                onClick={restart}
                disabled={isRestarting}>
                Restart
            </button>
        </>
    );
}
