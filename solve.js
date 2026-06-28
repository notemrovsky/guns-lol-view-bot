const { readFileSync } = require('fs');
const path = require('path');

const input = JSON.parse(process.argv[2]);
const { o09, d, _org_ts, _n, _2xa } = input;

const heap = new Array(128).fill(undefined);
heap.push(undefined, null, true, false);
let heap_next = heap.length;

function addHeapObject(obj) {
    if (heap_next === heap.length) heap.push(heap.length + 1);
    const idx = heap_next;
    heap_next = heap[idx];
    heap[idx] = obj;
    return idx;
}

function getObject(idx) { return heap[idx]; }

function dropObject(idx) {
    if (idx < 132) return;
    heap[idx] = heap_next;
    heap_next = idx;
}

function takeObject(idx) {
    const ret = getObject(idx);
    dropObject(idx);
    return ret;
}

const decoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });
const encoder = new TextEncoder();

let wasm;
let cachedMem = null;
let cachedDV = null;

function getMem() {
    if (!cachedMem || cachedMem.byteLength === 0)
        cachedMem = new Uint8Array(wasm.memory.buffer);
    return cachedMem;
}

function getDV() {
    if (!cachedDV || cachedDV.buffer !== wasm.memory.buffer)
        cachedDV = new DataView(wasm.memory.buffer);
    return cachedDV;
}

function getStr(ptr, len) {
    return decoder.decode(getMem().subarray(ptr >>> 0, (ptr >>> 0) + len));
}

let WASM_VECTOR_LEN = 0;

function passStr(arg) {
    const buf = encoder.encode(arg);
    const ptr = wasm.__wbindgen_export_0(buf.length, 1) >>> 0;
    getMem().subarray(ptr, ptr + buf.length).set(buf);
    WASM_VECTOR_LEN = buf.length;
    return ptr;
}

const imports = {
    wbg: {
        __wbg_new_405e22f390576ce2: () => addHeapObject({}),
        __wbg_set_3807d5f0bfc24aa7: (a, b, c) => {
            getObject(a)[takeObject(b)] = takeObject(c);
        },
        __wbindgen_number_new: (a) => addHeapObject(a),
        __wbindgen_object_clone_ref: (a) => addHeapObject(getObject(a)),
        __wbindgen_object_drop_ref: (a) => { takeObject(a); },
        __wbindgen_rethrow: (a) => { throw takeObject(a); },
        __wbindgen_string_new: (a, b) => addHeapObject(getStr(a, b)),
        __wbindgen_throw: (a, b) => { throw new Error(getStr(a, b)); },
    }
};

(async () => {
    const wasmPath = path.join(__dirname, 'gpp_gunslol_bg.wasm');
    const wasmBytes = readFileSync(wasmPath);
    const { instance } = await WebAssembly.instantiate(wasmBytes, imports);
    wasm = instance.exports;

    const p0 = passStr(o09); const l0 = WASM_VECTOR_LEN;
    const p1 = passStr(_org_ts); const l1 = WASM_VECTOR_LEN;
    const p2 = passStr(_n); const l2 = WASM_VECTOR_LEN;
    const p3 = passStr(_2xa); const l3 = WASM_VECTOR_LEN;

    const solver_ptr = wasm.gunssolver_new(p0, l0, parseInt(d), p1, l1, p2, l2, p3, l3);

    const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
    wasm.gunssolver_solve_pow(retptr, solver_ptr);
    const r0 = getDV().getInt32(retptr + 0, true);
    const r1 = getDV().getInt32(retptr + 4, true);
    const r2 = getDV().getInt32(retptr + 8, true);
    wasm.__wbindgen_add_to_stack_pointer(16);

    if (r2) {
        process.stderr.write(JSON.stringify({ error: String(takeObject(r1)) }));
        process.exit(1);
    }

    const result = takeObject(r0);
    process.stdout.write(JSON.stringify(result));
})();
