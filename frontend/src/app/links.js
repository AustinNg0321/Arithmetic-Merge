import Link from "next/link";

export default function GameModes() {
    return (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:border-emerald-200 hover:shadow-md">
                <h3 className="text-xl font-semibold text-gray-900">Solo Mode</h3>
                <p className="mt-2 text-gray-600">
                    Play at your own pace. Slide tiles to reach 67.
                </p>
                <Link
                    href="/solo"
                    className="mt-5 inline-flex rounded-lg bg-emerald-500 px-5 py-2.5 font-semibold text-white transition-colors hover:bg-emerald-700"
                >
                    Play Now
                </Link>
            </div>

            <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:border-emerald-200 hover:shadow-md">
                <h3 className="text-xl font-semibold text-gray-900">How It Works</h3>
                <p className="mt-2 text-gray-600">
                    Learn the merge rules and strategies.
                </p>
                <Link
                    href="#rules"
                    className="mt-5 inline-flex rounded-lg border border-emerald-200 bg-white px-5 py-2.5 font-semibold text-emerald-700 transition-colors hover:bg-emerald-50"
                >
                    View Rules
                </Link>
            </div>
        </div>
    );
}
