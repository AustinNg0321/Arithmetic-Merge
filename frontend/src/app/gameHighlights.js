function Tile({ children }) {
    return (
        <div className="flex h-12 w-12 items-center justify-center rounded-lg border border-gray-300 bg-blue-100 text-lg font-bold text-gray-800">
            {children}
        </div>
    );
}

function Chip({ children }) {
    return (
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700">
            {children}
        </span>
    );
}

export default function GameHighlights() {
    return (
        <section className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-900">Why this is interesting</h2>
            <p className="mt-3 text-gray-600">
                Arithmetic Merge adds just enough strategy to make each run feel like a small puzzle instead of a pure luck roll.
            </p>

            <div className="mt-5 flex flex-wrap gap-2">
                <Chip>Math-based merges</Chip>
                <Chip>Fast runs</Chip>
                <Chip>Session stats</Chip>
            </div>

            <div className="mt-8 rounded-xl border border-gray-100 bg-gray-50 p-4">
                <div className="flex flex-wrap items-center gap-3">
                    <Tile>8</Tile>
                    <Tile>+</Tile>
                    <Tile>_</Tile>
                    <Tile>0</Tile>
                    <span className="text-xl font-semibold text-gray-400">→</span>
                    <Tile>8</Tile>
                </div>
                <p className="mt-3 text-sm text-gray-500">Gaps are removed before combining</p>
            </div>

            <div className="mt-6 rounded-xl bg-emerald-50 p-4 text-center">
                <p className="text-xl font-semibold text-emerald-700">🎯 Reach 67 to win</p>
            </div>

            <div className="mt-6 text-gray-500">
                <p>↑ ↓ ← → to slide tiles</p>
            </div>
        </section>
    );
}
