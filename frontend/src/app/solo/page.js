"use client";

import { useEffect, useState } from "react";
import "./gameGrid.css";

function parse(num) {
    switch (num) {
        case 1001:
            return "+";
        case 1002:
            return "-";
        case 1003:
            return "*";
        case 1004:
            return " ";
        default:
            return num.toString();
    }
}

function Game({ curGame }) {
    const curGrid = curGame.grid;

    return (
        <div className="container mb-5 text-center">
            {curGrid.map((row, r) => (
                <div key={r} className="row flex">
                    {row.map((cell, c) => (
                        <div key={c} className="cell flex items-center justify-center font-bold m-1
                      bg-blue-100 border border-gray-300 aspect-square size-1/12 lg:size-16 
                        text-md lg:text-2xl rounded-sm lg:rounded-lg">
                            { parse(cell) }
                        </div>))}
                </div>
            ))}
        </div>  
    )
}

export default function Solo() {
    const [game, setGame] = useState(null);

    const fetchGame = () => {
        fetch("/api/solo", {
        credentials: "include"
        })
        .then((res) => res.json())
        .then((data) => setGame(data))
        .catch((err) => console.error(err));
    }

    const restart = () => {
        fetch("/api/restart", {
            method: "POST",
            credentials: "include"
        })
        .then((res) => res.json())
        .then((game) => setGame(game))
        .catch((err) => console.error(err));
    }

    const move = (dir) => {
        fetch(`/api/move`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "text/plain" },
            body: dir
        })
        .then((res) => res.json())
        .then((game) => setGame(game))
        .catch((err) => console.error(err));
    }

    useEffect(() => {
        function handleKeyDown(e) {
            let dir = "";
            switch (e.key) {
                case "ArrowUp":
                    dir = "up";
                    break;
                case "ArrowDown":
                    dir = "down";
                    break;
                case "ArrowLeft":
                    dir = "left";
                    break;
                case "ArrowRight":
                    dir = "right";
                    break;
                default:
                    break;
            }

            e.preventDefault();
            move(dir);
        }

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [game]) 

    useEffect(fetchGame, []);

    if (!game) {
        return <p>Loading Game ...</p>;
    }

    return (
        <>
            <Game curGame={game}/>
            <button className="restart pl-5 pr-5 pt-2.5 pb-2.5 text-lg rounded-md border 
            bg-emerald-500 text-white cursor-pointer hover:bg-emerald-700" onClick={restart}>
                Restart
            </button>
        </>
    );
}
