import Link from "next/link";

export default function Hero() {
    return (
        <section className="bg-gradient-to-b from-emerald-50 to-white py-16 text-center rounded-3xl">
            <div className="mx-auto max-w-2xl px-6">
                <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                    Arithmetic Merge
                </h1>
                <p className="mt-4 text-lg text-gray-600">
                    A sliding tile puzzle where numbers and operators collide. Reach 67 to win.
                </p>
                <div className="mt-8">
                    <Link
                        href="/solo"
                        className="inline-flex rounded-lg bg-emerald-500 px-8 py-3 text-lg font-semibold text-white transition-colors hover:bg-emerald-700"
                    >
                        Play Now
                    </Link>
                </div>
            </div>
        </section>
    );
}
