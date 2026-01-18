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

    const subgraphStack = [];

    lines.forEach(line => {
        line = line.trim();
        if (!line || line.startsWith('%%') || line.startsWith('graph ') || line.startsWith('flowchart ')) return;

        // Subgraph handling
        if (line.startsWith('subgraph ')) {
            const match = line.match(/subgraph\s+([^\s\[]+)/);
            const name = match ? match[1] : 'unknown';
            subgraphStack.push(name);
            return;
        }
        if (line === 'end') {
            subgraphStack.pop();
            return;
        }

        const currentSubgraph = subgraphStack.length > 0 ? subgraphStack[subgraphStack.length - 1] : null;

        // Edge handling
        // Split by generic arrow pattern
        // Matches A & B --> C & D
        const parts = line.split(/\s*[-=.]{1,4}(?:(?:\|.+?\|)|(?:.+?))?[-=.]{0,3}[>]\s*/);

        if (parts.length > 1) {
            for (let i = 0; i < parts.length - 1; i++) {
                const rawSourceGroup = parts[i].trim();
                const rawTargetGroup = parts[i+1].trim();

                if (!rawSourceGroup || !rawTargetGroup) continue;

                const sources = expandNodes(rawSourceGroup);
                const targets = expandNodes(rawTargetGroup);

                sources.forEach(source => {
                    targets.forEach(target => {
                        if (source && target) {
                            nodes.add(source);
                            nodes.add(target);
                            edges.push({ from: source, to: target });

                            if (currentSubgraph) {
                                if (!nodeSubgraphs.has(source) || isDefinition(rawSourceGroup)) {
                                    nodeSubgraphs.set(source, currentSubgraph);
                                }
                                if (!nodeSubgraphs.has(target) || isDefinition(rawTargetGroup)) {
                                    nodeSubgraphs.set(target, currentSubgraph);
                                }
                            }
                        }
                    });
                });
            }
        } else {
            // Standalone node or subgraph node definition
            // A[Label]
            const rawNode = parts[0].trim();
            const expanded = expandNodes(rawNode);
            expanded.forEach(node => {
                if (node) {
                    nodes.add(node);
                    if (currentSubgraph) {
                        nodeSubgraphs.set(node, currentSubgraph);
                    }
                }
            });
        }
    });

    return { nodes, edges, nodeSubgraphs };
}

function expandNodes(rawGroup) {
    // Handle 'A & B' syntax
    const parts = rawGroup.split('&');
    const nodes = [];
    parts.forEach(part => {
        const node = cleanNodeId(part.trim());
        if (node) nodes.push(node);
    });
    return nodes;
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
    const pathStack = []; // To track the current path for cycle reporting

    function dfs(node) {
        if (visiting.has(node)) {
            // Cycle detected
            const cyclePath = [...pathStack, node].join(' -> ');
            throw new Error(`Cycle detected: ${cyclePath}`);
        }
        if (memo.has(node)) return memo.get(node);

        visiting.add(node);
        pathStack.push(node);

        let maxPath = 0;
        const neighbors = adj.get(node) || [];

        for (const neighbor of neighbors) {
            try {
                const depth = dfs(neighbor);
                maxPath = Math.max(maxPath, depth);
            } catch (e) {
                if (e.message.startsWith('Cycle detected')) {
                    throw e;
                }
                throw e;
            }
        }

        pathStack.pop();
        visiting.delete(node);
        memo.set(node, 1 + maxPath);
        return 1 + maxPath;
    }

    let globalMax = 0;
    for (const node of nodes) {
        try {
            const d = dfs(node);
            globalMax = Math.max(globalMax, d);
        } catch (e) {
            if (e.message.startsWith('Cycle detected')) {
                throw e; // Propagate cycle error
            }
        }
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

        console.log(`\n📄 Analyzing: ${path.relative(SOURCE_DIR, file)}`);

        // Orphan check
        const connectedNodes = new Set();
        edges.forEach(e => {
            connectedNodes.add(e.from);
            connectedNodes.add(e.to);
        });

        nodes.forEach(node => {
            if (!connectedNodes.has(node)) {
                console.warn(`   ⚠️ WARNING: Orphaned node detected: ${node}`);
            }
        });

        let depth = 0;
        try {
            depth = calculateMaxDepth(nodes, edges);
            console.log(`   Nodes: ${nodeCount} (Limit: ${config.maxNodes})`);
            console.log(`   Depth: ${depth} (Limit: ${config.maxDepth})`);
        } catch (e) {
            console.error(`   ❌ VIOLATION: ${e.message}`);
            hasViolations = true;
            depth = Infinity; // Mark as infinite for logic
        }

        // Check 1: Max Nodes
        if (nodeCount > config.maxNodes) {
            console.error(`   ❌ VIOLATION: Node count ${nodeCount} exceeds limit ${config.maxNodes}`);
            hasViolations = true;
        }

        // Check 2: Max Depth (if not cycle)
        if (depth > config.maxDepth && depth !== Infinity) {
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
