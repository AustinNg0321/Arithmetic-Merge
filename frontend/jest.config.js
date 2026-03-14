export default {
    testEnvironment: "jest-environment-jsdom",
    transform: {
        "^.+\\.js$": "babel-jest",
    },
    setupFiles: ["jest-fetch-mock/setupJest", "./jest.setup.js"],
    testMatch: ["**/__tests__/**/*.test.js"],
    moduleNameMapper: {
        "^@/(.*)$": "<rootDir>/src/$1",
        "\\.css$": "<rootDir>/__mocks__/fileMock.js",
    },
};
