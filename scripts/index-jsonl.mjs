#!/usr/bin/env node
// Genera data/build/personas.offsets: offset en bytes de cada línea de personas.jsonl (+ fin de archivo).
// Solo para desarrollo local (PERSONAS_JSONL) o para servir el dataset sin Blobs.
import fs from 'node:fs';
const ruta = process.argv[2] || 'data/build/personas.jsonl';
const fd = fs.openSync(ruta, 'r');
const tam = fs.fstatSync(fd).size;
const offs = [0n];
const buf = Buffer.alloc(8 * 1024 * 1024);
let pos = 0;
while (pos < tam) {
  const n = fs.readSync(fd, buf, 0, buf.length, pos);
  for (let i = 0; i < n; i++) if (buf[i] === 10) offs.push(BigInt(pos + i + 1));
  pos += n;
}
if (offs[offs.length - 1] !== BigInt(tam)) offs.push(BigInt(tam));
const arr = new BigUint64Array(offs);
fs.writeFileSync(ruta.replace(/\.jsonl$/, '.offsets'), Buffer.from(arr.buffer));
console.log('líneas', offs.length - 1, '->', ruta.replace(/\.jsonl$/, '.offsets'));
