import { describe, test, expect } from "@jest/globals";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function readFile(...parts) {
  return fs.readFileSync(path.resolve(__dirname, "..", ...parts), "utf8");
}

describe("solo page contracts", () => {
  test("restart button is wired to restart handler and disabled by isRestarting", () => {
    const source = readFile("src", "app", "solo", "page.js");

    expect(source).toContain("onClick={restart}");
    expect(source).toContain("disabled={isRestarting}");
    expect(source).toContain("cursor-not-allowed");
  });

  test("keyboard controls map arrow keys to moves", () => {
    const source = readFile("src", "app", "solo", "page.js");

    expect(source).toContain('ArrowUp: "up"');
    expect(source).toContain('ArrowDown: "down"');
    expect(source).toContain('ArrowLeft: "left"');
    expect(source).toContain('ArrowRight: "right"');
    expect(source).toContain("directions[e.key]");
  });
});

describe("restart consistency contracts", () => {
  test("manual restart gates new local game on backend success path", () => {
    const source = readFile("src", "app", "solo", "gameContext.js");

    const start = source.indexOf("const restart = useCallback(async () => {");
    const end = source.indexOf("}, [abandonGame, verifyGame]);", start);
    const restartBlock = source.slice(start, end);

    expect(restartBlock).toContain("canRestart = await abandonGame(curGame);");
    expect(restartBlock).toContain("canRestart = await verifyGame(curGame);");
    expect(restartBlock).toContain("if (!canRestart) {");
    expect(restartBlock).toContain("const nextGame = createGame();");
    expect(restartBlock).toContain("commitGame(nextGame, []);");

    const guardIndex = restartBlock.indexOf("if (!canRestart) {");
    const commitIndex = restartBlock.indexOf("commitGame(nextGame, []);");
    expect(guardIndex).toBeGreaterThan(-1);
    expect(commitIndex).toBeGreaterThan(-1);
    expect(guardIndex).toBeLessThan(commitIndex);
  });

  test("verify and abandon helpers return explicit success booleans", () => {
    const source = readFile("src", "app", "solo", "gameContext.js");

    expect(source).toContain("return true;");
    expect(source).toContain("return false;");
    expect(source).toContain("Verification failed with status");
    expect(source).toContain("Abandon request failed with status");
  });

  test("terminal games trigger verification then delayed restart", () => {
    const source = readFile("src", "app", "solo", "gameContext.js");

    expect(source).toContain('if (!game || (game.state !== "Won" && game.state !== "Lost"))');
    expect(source).toContain("void verifyGame(gameRef.current);");
    expect(source).toContain("const timeoutId = window.setTimeout(() => restart(), 2000);");
  });
});

describe("statistics contracts", () => {
  test("statistics useEffect reads cache and fetches when cache is absent", () => {
    const source = readFile("src", "app", "statistics.js");

    expect(source).toContain("readStatisticsFromStorage()");
    expect(source).toContain("if (statistics && refetched) {");
    expect(source).toContain("fetchStatistics()");
    expect(source).toContain("setRefetched(true);");
    expect(source).toContain("writeStatisticsToStorage(data)");
    expect(source).toContain("broadcastStatistics(data)");
  });

  test("statistics updater event is subscribed and unsubscribed", () => {
    const source = readFile("src", "app", "statistics.js");

    expect(source).toContain("window.addEventListener(STATISTICS_UPDATED_EVENT");
    expect(source).toContain("window.removeEventListener(STATISTICS_UPDATED_EVENT");
  });
});
