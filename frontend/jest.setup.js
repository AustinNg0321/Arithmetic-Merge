import { randomUUID } from "crypto";
import { TextEncoder, TextDecoder } from "util";

if (!globalThis.crypto) {
    globalThis.crypto = {};
}
if (!globalThis.crypto.randomUUID) {
    globalThis.crypto.randomUUID = randomUUID;
}

if (!globalThis.TextEncoder) {
    globalThis.TextEncoder = TextEncoder;
}
if (!globalThis.TextDecoder) {
    globalThis.TextDecoder = TextDecoder;
}
