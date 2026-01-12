"use client";

import { useEffect, useState } from "react";
import GameModes from "./links";
import "./globals.css";

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
    )
}

export default function Home() {
    const [info, setInfo] = useState(null);

    useEffect(() => {
      fetch("/api/", {
        credentials: "include",
      })
        .then((res) => res.json())
        .then((data) => setInfo(data))
        .catch((err) => console.error(err));
    }, []);

    if (!info) {
        return <p>Loading ...</p>;
    }

    return (
        <>
            <Statistics data={info}/>
            <GameModes/>
        </>
    );
}

/*const styles = {
  container: { padding: 20, textAlign: "center" },
  title: { fontSize: 32, marginBottom: 20 },
  grid: {
    display: "grid",
    gridTemplateRows: `repeat(${ROWS}, ${TILE_SIZE}px)`,
    gridTemplateColumns: `repeat(${COLS}, ${TILE_SIZE}px)`,
    gap: 6,
    justifyContent: "center",
    marginBottom: 20,
    position: "relative",
  },
  tile: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    border: "1px solid #ccc",
    fontSize: 24,
    fontWeight: "bold",
    boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
    width: TILE_SIZE,
    height: TILE_SIZE,
  },
  controls: { marginTop: 20 },
  button: {
    padding: "10px 20px",
    fontSize: 18,
    borderRadius: 6,
    border: "none",
    backgroundColor: "#0070f3",
    color: "white",
    cursor: "pointer",
  },
};*/
