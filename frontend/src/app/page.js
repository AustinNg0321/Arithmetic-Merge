"use client";
import GameModes from "./links";
import dynamic from "next/dynamic";
import "./globals.css";

const StatisticsContainer = dynamic(
  () => import("./statistics"),
  { ssr: false }
);

export default function Home() {
    return (
        <>
            <StatisticsContainer/>
            <GameModes/>
        </>
    );
}
