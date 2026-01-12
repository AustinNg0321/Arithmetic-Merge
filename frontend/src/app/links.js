import Link from "next/link";
import "./globals.css"

export default function GameModes() {
    return (
        <>
            <Link href="/solo" className="pl-5 pr-5 pt-2.5 pb-2.5 text-lg rounded-md border bg-emerald-500 text-white cursor-pointer hover:bg-emerald-700">
                Play Solo
            </Link>
        </>
    );
}