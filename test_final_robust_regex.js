const MERMAID_EDGE_RE = (function() {
  const b = '!';
  const dash = '\\x2D';
  const gt = '\\x3E';
  const dot = '\\x2E';
  const eq = '=';

  // Arrowheads and lines
  const arr = dash + dash + '(?:' + b + '?)' + gt; // --> or --!>
  const line3 = dash + dash + dash; // ---
  const line2 = dash + dash; // --

  const d_arr = eq + eq + gt; // ==>
  const d_line3 = eq + eq + eq; // ===
  const d_line2 = eq + eq; // ==

  const p_arr = dash + dot + dash + gt; // -.->
  const p_line3 = dash + dot + dash; // -.-
  const p_line2 = dash + dot; // -.

  // Labels: everything between lines/arrows
  const label = '[^' + gt + '|]+?';

  const labeled = '(?:' + line2 + '|' + d_line2 + '|' + p_line2 + ')' + label + '(?:' + arr + '|' + line3 + '|' + d_arr + '|' + d_line3 + '|' + p_arr + '|' + p_line3 + ')';

  const arrows_with_label_brackets = '(?:' + arr + '|' + line3 + '|' + d_arr + '|' + d_line3 + '|' + p_arr + '|' + p_line3 + ')\\|[^|]+\\|';

  const simple = [
    '\\x3C' + arr, '\\x3C' + d_arr, '\\x3C' + dash + dot + dash + gt, // <--> etc
    '\\x3C' + line2, '\\x3C' + d_line2, '\\x3C' + p_line2, // <-- etc
    arr, d_arr, p_arr,
    line3, d_line3, p_line3,
    '\\x3C' + gt, dash + gt, '\\x3C' + dash // <->, ->, <-
  ];

  const combined = '(' + [labeled, arrows_with_label_brackets, ...simple].join('|') + ')';
  return new RegExp('\\s*' + combined + '\\s*');
})();

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
    "A -- my-file.js --> B",
    "X --!> Y"
];

cases.forEach(line => {
    const parts = line.split(MERMAID_EDGE_RE).map(p => p.trim()).filter(p => p !== "");
    console.log(`Line: "${line}" -> Parts:`, parts);
});
