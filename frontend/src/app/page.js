"use client";
import { Rules } from "./rules";
import GameModes from "./links";
import dynamic from "next/dynamic";
import Hero from "./hero";
import GameHighlights from "./gameHighlights";
import "./globals.css";

const StatisticsContainer = dynamic(
  () => import("./statistics"),
  { ssr: false }
);


export default function Home() {
    return (
        <main className="mx-auto max-w-4xl px-6 py-12">
            <Hero />
            <div className="mt-10">
                <StatisticsContainer />
            </div>
            <section className="mt-10 grid grid-cols-1 gap-8 lg:grid-cols-2">
                <Rules />
                <GameHighlights />
            </section>
            <section className="mt-10">
                <GameModes />
            </section>
        </main>
    );
}
