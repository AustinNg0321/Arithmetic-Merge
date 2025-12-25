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
        <div className="container">
            {curGrid.map((row, r) => (
                <div key={r} className="row">
                    {row.map((cell, c) => (<div key={c} className="cell">{ parse(cell) }</div>))}
                </div>
            ))}
        </div>  
    )
}

export default function Solo() {
    const [game, setGame] = useState(null);

    useEffect(() => {
        fetch("/api/solo", {
        credentials: "include"
        })
        .then((res) => res.json())
        .then((data) => setGame(data))
        .catch((err) => console.error(err));
    }, []);

    if (!game) {
        return <p>Loading game...</p>;
    }

    return <Game curGame={game}/>;
}