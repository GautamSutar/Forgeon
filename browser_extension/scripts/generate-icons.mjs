// Generates the extension's toolbar icons as real PNG files, hand-encoded
// via zlib — no image-processing dependency needed for a simple flat-color
// glyph. Run with `npm run generate-icons`.
import { deflateSync } from "node:zlib";
import { writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = resolve(__dirname, "..", "public", "icons");

const BG = [37, 99, 235]; // blue-600
const FG = [255, 255, 255];

function crc32(buf) {
  let c;
  const table = crc32.table ?? (crc32.table = makeTable());
  let crc = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    c = (crc ^ buf[i]) & 0xff;
    crc = (crc >>> 8) ^ table[c];
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function makeTable() {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
}

function chunk(type, data) {
  const typeBuf = Buffer.from(type, "ascii");
  const lenBuf = Buffer.alloc(4);
  lenBuf.writeUInt32BE(data.length, 0);
  const crcBuf = Buffer.alloc(4);
  crcBuf.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
  return Buffer.concat([lenBuf, typeBuf, data, crcBuf]);
}

// Draws a simple rounded-ish "checkmark-in-square" glyph so the icon reads
// as "reviewed / approved" at a glance, matching the human-approval theme.
function pixelAt(x, y, size) {
  const margin = Math.round(size * 0.16);
  const inSquare = x >= margin && x < size - margin && y >= margin && y < size - margin;
  if (!inSquare) return null;

  // Checkmark via two line segments, scaled to icon size.
  const nx = (x - margin) / (size - 2 * margin);
  const ny = (y - margin) / (size - 2 * margin);
  const onStroke1 = Math.abs(ny - (1.5 * nx + 0.15)) < 0.14 && nx >= 0.1 && nx <= 0.42;
  const onStroke2 = Math.abs(ny - (-1.1 * nx + 1.05)) < 0.14 && nx >= 0.38 && nx <= 0.85;
  if (onStroke1 || onStroke2) return FG;
  return BG;
}

function buildPng(size) {
  const rowBytes = size * 4 + 1;
  const raw = Buffer.alloc(rowBytes * size);
  for (let y = 0; y < size; y++) {
    raw[y * rowBytes] = 0; // filter type: none
    for (let x = 0; x < size; x++) {
      const [r, g, b] = pixelAt(x, y, size) ?? BG;
      const offset = y * rowBytes + 1 + x * 4;
      raw[offset] = r;
      raw[offset + 1] = g;
      raw[offset + 2] = b;
      raw[offset + 3] = 255;
    }
  }

  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type: RGBA
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;

  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const idat = deflateSync(raw);

  return Buffer.concat([
    signature,
    chunk("IHDR", ihdr),
    chunk("IDAT", idat),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

mkdirSync(OUT_DIR, { recursive: true });
for (const size of [16, 32, 48, 128]) {
  const png = buildPng(size);
  const path = resolve(OUT_DIR, `icon${size}.png`);
  writeFileSync(path, png);
  console.log(`wrote ${path} (${png.length} bytes)`);
}
