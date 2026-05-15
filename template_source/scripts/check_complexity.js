// Jules Code Team Template
// Copyright (C) 2026  MnemOnicE
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

const fs = require('node:fs');
const path = require('node:path');

// Constants
// Matches Mermaid arrow patterns (e.g., A -> B, A -- Label -> B, A --- B, A <-> B).
// Supports directed, undirected, and bi-directional edges with optional labels.
// Designed to avoid consuming nodes in chained definitions (e.g., A --- B -> C).
// Matches Mermaid arrow patterns (e.g., A -> B, A -- Label -> B, A --- B, A <-> B).
// Supports directed, undirected, and bi-directional edges with optional labels.
// Designed to avoid consuming nodes in chained definitions (e.g., A --- B -> C).
// Static regex for Mermaid edges to satisfy security scanners and ensure ReDoS safety.
// Supports: <==>, <--> , <->, --!>, -->, ---, ==>, ===, <--, <==, <-., -.-, -.->, ->, <-
// Hex escapes (\x3E for '>', \x2E for '.') are used to avoid CodeQL js/html-comment-confusion.
const MERMAID_EDGE_RE = /\s*(<==\x3E|<--\x3E|--!\x3E|-\x2E-\x3E|<-\x3E|--\x3E|---|\x3D\x3D\x3E|\x3D\x3D\x3D|<--|<==|<-\x2E|-.-|-\x3E|<-)\s*/;

// Configuration
const CONFIG_FILE = path.join(__dirname, '../.mermaid-sonar.json');
const SOURCE_DIR = path.join(__dirname, '../');

function getAllMermaidFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);

    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            if (file !== 'node_modules' && file !== '.git' && file !== 'ingests' && file !== 'tests' && file !== 'mocks') {
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

function shouldSkipLine(line) {
    return !line || line.startsWith('%%') || line.startsWith('graph ') || line.startsWith('flowchart ');
}

function handleSubgraph(line, stack) {
    if (line.startsWith('subgraph ')) {
        const match = line.match(/subgraph\s+([^\s\[]+)/);
        const name = match ? match[1] : 'unknown';
        stack.push(name);
        return true;
    }
    if (line === 'end') {
        stack.pop();
        return true;
    }
    return false;
}

function processEdgeParts(parts, nodes, edges, nodeSubgraphs, currentSubgraph) {
    // When using capturing split, parts is [nodeGroup0, token0, nodeGroup1, token1, ...]
    for (let i = 0; i < parts.length - 2; i += 2) {
        const rawSourceGroup = parts[i].trim();
        const token = parts[i+1];
        const rawTargetGroup = parts[i+2].trim();

        if (!rawSourceGroup || !rawTargetGroup) continue;

        const sources = expandNodes(rawSourceGroup);
        const targets = expandNodes(rawTargetGroup);

        const hasLeft = token.includes('<');
        const hasRight = token.includes('>');
        const isLeft = hasLeft && !hasRight;

        sources.forEach(source => {
            targets.forEach(target => {
                if (source && target) {
                    nodes.add(source);
                    nodes.add(target);

                    if (isLeft) {
                        // Reverse arrow: A <- B
                        edges.push({ from: target, to: source });
                    } else {
                        // Forward, undirected, or bi-directional: A -> B, A --- B, A <-> B.
                        // For bi-directional edges, we only add one direction to avoid
                        // trivial cycles during complexity/depth checks.
                        edges.push({ from: source, to: target });
                    }

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
}

function processNodeLine(line, nodes, nodeSubgraphs, currentSubgraph) {
    // Standalone node or subgraph node definition
    // A[Label]
    const rawNode = line.trim();
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

function parseMermaid(content) {
    const lines = content.split('\n');
    const nodes = new Set();
    const edges = [];
    const nodeSubgraphs = new Map(); // node -> subgraphName

    const subgraphStack = [];

    lines.forEach(line => {
        line = line.trim();
        if (shouldSkipLine(line)) return;

        if (handleSubgraph(line, subgraphStack)) return;

        const currentSubgraph = subgraphStack.length > 0 ? subgraphStack[subgraphStack.length - 1] : null;

        // Edge handling
        // Split by generic arrow pattern (e.g., A & B -> C & D)
        const parts = line.split(MERMAID_EDGE_RE);

        if (parts.length > 1) {
            processEdgeParts(parts, nodes, edges, nodeSubgraphs, currentSubgraph);
        } else {
            // Standalone node or subgraph node definition
            processNodeLine(parts[0], nodes, nodeSubgraphs, currentSubgraph);
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
    // Mermaid nodes can be prefixed/suffixed with labels when splitting by arrows.
    // e.g., "A -- label" or "|label| B"
    let id = raw.trim();

    // Strip leading label brackets/pipes: -->|label| B
    if (id.startsWith('|')) {
        const nextPipe = id.indexOf('|', 1);
        if (nextPipe !== -1) {
            id = id.substring(nextPipe + 1).trim();
        }
    }

    // Strip trailing label lines: A -- label -->
    // Only strip if the marker is preceded by whitespace to avoid breaking IDs like svc--blue.
    ['--', '=='].forEach(marker => {
        const idx = id.search(new RegExp('\\s' + marker));
        if (idx !== -1) {
            id = id.substring(0, idx).trim();
        }
    });

    // Remove shapes: A[Text] -> A, A("Text") -> A, A{Text} -> A
    // Extract alphanumeric ID by manual traversal to avoid ReDoS hotspots.
    let cleanId = "";
    const allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-";
    for (let i = 0; i < id.length; i++) {
        const char = id[i];
        if (allowed.includes(char)) {
            cleanId += char;
        } else {
            break;
        }
    }

    return cleanId.length > 0 ? cleanId : null;
}

function isDefinition(raw) {
    // Check if the raw string contains definition characters like [, (, {
    return raw.includes('(') || raw.includes('[') || raw.includes('{');
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
            const depth = dfs(neighbor);
            maxPath = Math.max(maxPath, depth);
        }

        pathStack.pop();
        visiting.delete(node);
        memo.set(node, 1 + maxPath);
        return 1 + maxPath;
    }

    let globalMax = 0;
    for (const node of nodes) {
        const d = dfs(node);
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

if (require.main === module) {
    checkComplexity();
}

module.exports = {
    getAllMermaidFiles,
    parseMermaid,
    expandNodes,
    cleanNodeId,
    isDefinition,
    calculateMaxDepth,
    checkComplexity
};
