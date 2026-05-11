const dash = '\x2D';
const gt = '\x3E';
const dot = '\x2E';
const arrow = dash + dash + gt;
const patterns = [
    '(?:\x2D\x2D|==|\x2D\x2E)(?:(?:\\|[^|]+\\|)|(?:[^' + gt + '|]+?))?(?:' + arrow + '|\x2D\x2D\x2D|==\x3E|===|\x2E\x2D\x3E|\x2E\x2D)',
    '\x3C' + arrow, '\x3C==\x3E', '\x3C\x2D\x2E\x2D\x3E', '\x3C\x2D\x2D', '\x3C==', '\x3C\x2D\x2E', '\x3C\x2D\x3E',
    arrow, '\x2D\x2D\x2D', '==\x3E', '===', '\x2D\x2E\x2D\x3E', '\x2D\x2E\x2D', '\x2D\x3E', '\x3C\x2D'
];
const MERMAID_EDGE_RE = new RegExp('\\s*(' + patterns.join('|') + ')(?:\\|[^|]+\\|)?\\s*');

const cases = [
    "A --> B --> C",
    "D --- E --- F",
    "G -- label --- H -- label --> I",
    "J -> K -> L",
    "M <-> N <-> O",
    "P <-- Q --> R",
    "S <==> T",
    "A -->|label| B",
    "C ---|label| D",
    "A -- my-file.js --> B"
];

cases.forEach(line => {
    const parts = line.split(MERMAID_EDGE_RE).map(p => p.trim()).filter(p => p !== "");
    console.log(`Line: "${line}" -> Parts:`, parts);
});
