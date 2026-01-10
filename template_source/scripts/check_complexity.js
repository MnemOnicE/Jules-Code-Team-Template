const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG_FILE = path.join(__dirname, '../.mermaid-sonar.json');
const SOURCE_DIR = path.join(__dirname, '../');

function getAllMermaidFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);

    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            if (file !== 'node_modules' && file !== '.git' && file !== 'ingests') {
                getAllMermaidFiles(filePath, fileList);
            }
        } else {
            if (path.extname(file) === '.mmd') {
                fileList.push(filePath);
            }
        }
    });

    return fileList;
}

function parseMermaid(content) {
    const lines = content.split('\n');
    const nodes = new Set();
    const edges = [];
    const nodeSubgraphs = new Map(); // node -> subgraphName

    let currentSubgraph = null;

    // Regex for edges: capture left, connection, right
    // Matches patterns like: A --> B, A -.-> B, A == B, A -- text --> B, A -->|text| B
    // We split by connection operators.
    const edgeRegex = /\s(={1,}|-{1,}|\.{1,})(-|>|\|)\s/;

    lines.forEach(line => {
        line = line.trim();
        if (!line || line.startsWith('%%') || line.startsWith('graph ') || line.startsWith('flowchart ')) return;

        // Subgraph handling
        if (line.startsWith('subgraph ')) {
            const match = line.match(/subgraph\s+([^\s\[]+)/);
            if (match) currentSubgraph = match[1];
            return;
        }
        if (line === 'end') {
            currentSubgraph = null;
            return;
        }

        // Edge handling
        // We look for connection tokens.
        // Simplified approach: Split by common arrow patterns.
        // Note: Mermaid arrows can be complex. We'll target standard architecture arrows.
        // A --> B
        // A -.-> B
        // A ==> B
        // We will try to identify parts.

        // This regex attempts to find the arrow separator.
        // It looks for a sequence of -, ., or = ending with > or followed by text and >
        // Case: A --> B (match -->)
        // Case: A -.-> B (match -.->)
        // Case: A -- text --> B (Complex)

        // Let's use a simpler heuristic for this template: Split by connection-like strings.
        // We assume one edge per line for simplicity, or chained A --> B --> C

        // Split by generic arrow pattern
        const parts = line.split(/\s*[-=.]{1,4}(?:(?:\|.+?\|)|(?:.+?))?[-=.]{0,3}[>]\s*/);

        if (parts.length > 1) {
            for (let i = 0; i < parts.length - 1; i++) {
                const rawSource = parts[i].trim();
                const rawTarget = parts[i+1].trim();

                if (!rawSource || !rawTarget) continue;

                const source = cleanNodeId(rawSource);
                const target = cleanNodeId(rawTarget);

                if (source && target) {
                    nodes.add(source);
                    nodes.add(target);
                    edges.push({ from: source, to: target });

                    if (currentSubgraph) {
                        // Assuming nodes are defined/used inside the subgraph block
                        // Note: Mermaid allows defining nodes outside and using inside.
                        // But usually in subgraphs, nodes appear there.
                        // We map node to the LAST subgraph it was seen in or declared.
                         if (!nodeSubgraphs.has(source) || isDefinition(rawSource)) {
                             nodeSubgraphs.set(source, currentSubgraph);
                         }
                         if (!nodeSubgraphs.has(target) || isDefinition(rawTarget)) {
                             nodeSubgraphs.set(target, currentSubgraph);
                         }
                    }
                }
            }
        } else {
            // Standalone node or subgraph node definition
            // A[Label]
            const rawNode = parts[0].trim();
            const node = cleanNodeId(rawNode);
            if (node) {
                nodes.add(node);
                if (currentSubgraph) {
                    nodeSubgraphs.set(node, currentSubgraph);
                }
            }
        }
    });

    return { nodes, edges, nodeSubgraphs };
}

function cleanNodeId(raw) {
    // Remove labels: A[Text] -> A, A("Text") -> A, A{Text} -> A
    // Also remove leading/trailing whitespace
    // Matches start of string, captures ID, stops at start of bracket/paren
    const match = raw.match(/^([a-zA-Z0-9_\-]+)/);
    return match ? match[1] : null;
}

function isDefinition(raw) {
    // Check if the raw string contains definition characters like [, (, {
    return /[\(\[\{]/.test(raw);
}

function calculateMaxDepth(nodes, edges) {
    const adj = new Map();
    nodes.forEach(n => adj.set(n, []));
    edges.forEach(e => {
        if (!adj.has(e.from)) adj.set(e.from, []);
        adj.get(e.from).push(e.to);
    });

    const memo = new Map();
    const visiting = new Set();

    function dfs(node) {
        if (visiting.has(node)) return Infinity; // Cycle detected
        if (memo.has(node)) return memo.get(node);

        visiting.add(node);

        let maxPath = 0;
        const neighbors = adj.get(node) || [];

        for (const neighbor of neighbors) {
            const depth = dfs(neighbor);
            if (depth === Infinity) {
                visiting.delete(node);
                return Infinity;
            }
            maxPath = Math.max(maxPath, depth);
        }

        visiting.delete(node);
        memo.set(node, 1 + maxPath);
        return 1 + maxPath;
    }

    let globalMax = 0;
    for (const node of nodes) {
        const d = dfs(node);
        if (d === Infinity) return Infinity; // Cycle
        globalMax = Math.max(globalMax, d);
    }

    return globalMax;
}

function checkComplexity() {
    console.log('🔍 Running Mermaid-Sonar Complexity Check...');

    if (!fs.existsSync(CONFIG_FILE)) {
        console.error('❌ Config file not found:', CONFIG_FILE);
        process.exit(1);
    }

    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    console.log(`✅ Loaded configuration: maxNodes=${config.maxNodes}, maxDepth=${config.maxDepth}`);

    const files = getAllMermaidFiles(SOURCE_DIR);
    console.log(`📂 Found ${files.length} .mmd files.`);

    let hasViolations = false;

    files.forEach(file => {
        const content = fs.readFileSync(file, 'utf8');
        const { nodes, edges, nodeSubgraphs } = parseMermaid(content);
        const nodeCount = nodes.size;
        const depth = calculateMaxDepth(nodes, edges);

        console.log(`\n📄 Analyzing: ${path.relative(SOURCE_DIR, file)}`);
        console.log(`   Nodes: ${nodeCount} (Limit: ${config.maxNodes})`);
        console.log(`   Depth: ${depth === Infinity ? 'Cycle Detected' : depth} (Limit: ${config.maxDepth})`);

        // Check 1: Max Nodes
        if (nodeCount > config.maxNodes) {
            console.error(`   ❌ VIOLATION: Node count ${nodeCount} exceeds limit ${config.maxNodes}`);
            hasViolations = true;
        }

        // Check 2: Max Depth
        if (depth > config.maxDepth) {
            console.error(`   ❌ VIOLATION: Depth ${depth} exceeds limit ${config.maxDepth}`);
            hasViolations = true;
        }

        // Check 3: Forbidden Imports
        if (config.forbiddenImports) {
            config.forbiddenImports.forEach(rule => {
                edges.forEach(edge => {
                    const sourceSub = nodeSubgraphs.get(edge.from);
                    const targetSub = nodeSubgraphs.get(edge.to);

                    if (sourceSub === rule.from && targetSub === rule.to) {
                        console.error(`   ❌ VIOLATION: Forbidden import from '${rule.from}' to '${rule.to}' detected (Edge: ${edge.from} -> ${edge.to})`);
                        hasViolations = true;
                    }
                });
            });
        }
    });

    if (hasViolations) {
        console.error('\n❌ Verification Failed: Complexity violations found.');
        process.exit(1);
    } else {
        console.log('\n✅ Verification Passed: No complexity violations found.');
    }
}

checkComplexity();
