import { describe, test, expect, beforeEach, afterEach, jest } from "@jest/globals";
import fetchMock from "jest-fetch-mock";
import {
    verifyOnServer,
    abandonOnServer,
    fetchStatistics,
    readStatisticsFromStorage,
    writeStatisticsToStorage,
    updateStatisticsFromOutcome,
} from "../src/app/solo/gameContext.js";

let consoleErrorSpy;

beforeEach(() => {
    fetchMock.resetMocks();
    sessionStorage.clear();
    consoleErrorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
});

afterEach(() => {
    consoleErrorSpy.mockRestore();
});

// ─── verifyOnServer ───────────────────────────────────────────────────────────

describe("verifyOnServer", () => {
    test("returns true on 200", async () => {
        fetchMock.mockResponseOnce("{}", { status: 200 });
        await expect(verifyOnServer("seed-1", ["up", "left"])).resolves.toBe(true);
    });

    test("throws on non-200", async () => {
        fetchMock.mockResponseOnce("", { status: 500 });
        await expect(verifyOnServer("seed-1", [])).rejects.toThrow(
            "Verification failed with status 500",
        );
    });

    test("POSTs seed and moves to the verify endpoint", async () => {
        fetchMock.mockResponseOnce("{}", { status: 200 });
        await verifyOnServer("abc", ["up", "down"]);

        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toMatch(/\/api\/verify$/);
        expect(options.method).toBe("POST");
        expect(JSON.parse(options.body)).toEqual({ seed: "abc", moves: ["up", "down"] });
    });

    test("sends credentials: include", async () => {
        fetchMock.mockResponseOnce("{}", { status: 200 });
        await verifyOnServer("s", []);
        const [, options] = fetchMock.mock.calls[0];
        expect(options.credentials).toBe("include");
    });
});

// ─── abandonOnServer ──────────────────────────────────────────────────────────

describe("abandonOnServer", () => {
    test("returns true on 200", async () => {
        fetchMock.mockResponseOnce("{}", { status: 200 });
        await expect(abandonOnServer("seed-2", ["left"])).resolves.toBe(true);
    });

    test("throws on non-200", async () => {
        fetchMock.mockResponseOnce("", { status: 503 });
        await expect(abandonOnServer("seed-2", [])).rejects.toThrow(
            "Abandon request failed with status 503",
        );
    });

    test("POSTs seed and moves to the restart endpoint", async () => {
        fetchMock.mockResponseOnce("{}", { status: 200 });
        await abandonOnServer("xyz", ["right", "up"]);

        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toMatch(/\/api\/restart$/);
        expect(options.method).toBe("POST");
        expect(JSON.parse(options.body)).toEqual({ seed: "xyz", moves: ["right", "up"] });
    });
});

// ─── fetchStatistics ──────────────────────────────────────────────────────────

describe("fetchStatistics", () => {
    test("returns parsed JSON on 200", async () => {
        const payload = { user_id: "u1", wins: 3, losses: 1, abandoned: 0 };
        fetchMock.mockResponseOnce(JSON.stringify(payload), { status: 200 });
        await expect(fetchStatistics()).resolves.toEqual(payload);
    });

    test("throws on non-200", async () => {
        fetchMock.mockResponseOnce("", { status: 401 });
        await expect(fetchStatistics()).rejects.toThrow("Failed to fetch statistics with status 401");
    });
});

// ─── storage helpers ──────────────────────────────────────────────────────────

describe("readStatisticsFromStorage / writeStatisticsToStorage", () => {
    test("returns null when nothing is stored", () => {
        expect(readStatisticsFromStorage()).toBeNull();
    });

    test("round-trips a valid statistics object", () => {
        const stats = { user_id: "u1", wins: 2, losses: 1, abandoned: 3 };
        writeStatisticsToStorage(stats);
        expect(readStatisticsFromStorage()).toEqual(stats);
    });

    test("throws on malformed cached value", () => {
        sessionStorage.setItem("statistics", JSON.stringify({ bad: true }));
        expect(() => readStatisticsFromStorage()).toThrow("Invalid cached statistics payload");
    });
});

// ─── updateStatisticsFromOutcome ──────────────────────────────────────────────

describe("updateStatisticsFromOutcome", () => {
    const base = { user_id: "u1", wins: 0, losses: 0, abandoned: 0 };

    test("increments wins on Won", async () => {
        writeStatisticsToStorage(base);
        await updateStatisticsFromOutcome("Won");
        expect(readStatisticsFromStorage()).toMatchObject({ wins: 1, losses: 0, abandoned: 0 });
    });

    test("increments losses on Lost", async () => {
        writeStatisticsToStorage(base);
        await updateStatisticsFromOutcome("Lost");
        expect(readStatisticsFromStorage()).toMatchObject({ wins: 0, losses: 1, abandoned: 0 });
    });

    test("increments abandoned on In Progress", async () => {
        writeStatisticsToStorage(base);
        await updateStatisticsFromOutcome("In Progress");
        expect(readStatisticsFromStorage()).toMatchObject({ wins: 0, losses: 0, abandoned: 1 });
    });

    test("falls back to fetch when cache is absent", async () => {
        const fetched = { user_id: "u2", wins: 5, losses: 2, abandoned: 1 };
        fetchMock.mockResponseOnce(JSON.stringify(fetched), { status: 200 });
        await updateStatisticsFromOutcome("Won");
        expect(readStatisticsFromStorage()).toEqual(fetched);
    });

    test("cache miss with failed fetch rejects without updating storage", async () => {
        fetchMock.mockRejectOnce(new Error("Network error"));
        await expect(updateStatisticsFromOutcome("Won")).rejects.toThrow("Network error");
        expect(readStatisticsFromStorage()).toBeNull();
    });
});
