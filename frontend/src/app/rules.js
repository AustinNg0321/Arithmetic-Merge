import { useState } from "react";

function Section({ title, children }) {
    return (
        <div>
            <h3 className="font-semibold text-gray-700 mb-1">{title}</h3>
            <ul className="list-disc list-inside space-y-1">
                {children}
            </ul>
        </div>
    );
}

function Li({ children }) {
    return <li className="text-gray-600">{children}</li>;
}

function Mono({ children }) {
    return <span className="font-mono bg-gray-100 px-1 rounded">{children}</span>;
}

export function BriefRules() {
    return (
        <>
            <div className="space-y-2 text-gray-600">
                <p>Slide tiles up, down, left, or right to combine them.</p>
                <p>When a number, operator, and number line up (e.g. <Mono>3 + 4</Mono>), they evaluate into a single
                tile (<Mono>7</Mono>).</p>
                <p>Two new tiles appear after every move.</p>
            </div>
            <div className="mt-4 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                <p className="font-semibold text-emerald-700">Goal: Create a tile with the value 67.</p>
            </div>
            <div className="mt-4 text-gray-600">
                <p className="font-semibold text-gray-700 mb-1">You lose if:</p>
                <ul className="list-disc list-inside space-y-1">
                    <Li>No valid moves remain</Li>
                    <Li>Any tile exceeds <Mono>1000</Mono> or drops below <Mono>-1000</Mono></Li>
                </ul>
            </div>
        </>
    )
}

export function AdditionalRules() {
    return (
        <div className="space-y-4 text-gray-600">
            <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                <p className="font-semibold text-emerald-700">
                    Objective: Get a tile with the value 67 to appear on the board.
                </p>
            </div>

            <Section title="How to Play">
                <Li>Slide all tiles in one of four directions: up, down, left, or right</Li>
                <Li>After each move, 2 new tiles are generated — 67% chance of being an operator 
                    (<Mono>+</Mono> or <Mono>-</Mono>), 33% chance of being a digit (<Mono>0-9</Mono>)</Li>
            </Section>

            <Section title="How Tiles Combine">
                <Li>When sliding, empty gaps are removed and tiles collapse toward the slide direction</Li>
                <Li>When a number, operator, and number are adjacent (e.g. <Mono>3 + 4</Mono>), they evaluate into 
                a single tile (<Mono>7</Mono>) — even if there were gaps between them before collapsing</Li>
                <Li>Only one operation is evaluated per triplet per move — numbers without an operator between them 
                    do not chain (e.g. <Mono>1 + 2 3</Mono> → <Mono>3 3</Mono>, not <Mono>6</Mono>)</Li>
                <Li>Consecutive identical operators collapse into one (e.g. <Mono>+ + +</Mono> → <Mono>+</Mono>)</Li>
            </Section>

            <Section title="Slide Direction and Order">
                <Li>Operations are always evaluated in the slide direction — left/up evaluates leftmost or topmost first,
                    right/down evaluates rightmost or bottommost first</Li>
                <Li>Slide left: <Mono>1 + 2 + 3</Mono> → <Mono>3 + 3</Mono> (1+2 evaluated first)</Li>
                <Li>Slide right: <Mono>1 + 2 + 3</Mono> → <Mono>1 + 5</Mono> (2+3 evaluated first)</Li>
                <Li>Slide right: <Mono>5 - 4</Mono> → <Mono>1</Mono>, not <Mono>-1</Mono> 
                (always left operand minus right)</Li>
            </Section>

            <Section title="Losing Conditions">
                <Li>No valid moves remain (all slides would result in the same board)</Li>
                <Li>Any number tile goes out of bounds (below <Mono>-1000</Mono> or above <Mono>1000</Mono>)</Li>
            </Section>
        </div>
    );
}

export function Rules() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>  
            <div className="m-8 max-w-md p-6 bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-gray-800">How to Play</h2>
                    <button
                        onClick={() => setIsOpen(true)}
                        className="w-6 h-6 rounded-full bg-gray-200 text-gray-600 text-sm font-bold hover:bg-gray-300"
                    >
                        ?
                    </button>
                </div>
                <BriefRules />
            </div>

            {/* modal overlay */}
            {isOpen && (
                <div className="overflow-y-auto fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center  z-50">
                    <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
                        <h2 className="text-2xl font-bold mb-4">Full Rules</h2>
                            <AdditionalRules />
                        <button className="mt-5 pl-5 pr-5 pt-2.5 pb-2.5 text-lg rounded-md border bg-emerald-500 
                        text-white cursor-pointer hover:bg-emerald-700"onClick={() => setIsOpen(false)}>Close</button>
                    </div>
                </div>
            )}
        </>
    );
}
