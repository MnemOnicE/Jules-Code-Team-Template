const assert = require('assert');
const { calculateMaxDepth, parseMermaid, cleanNodeId, expandNodes } = require('../scripts/check_complexity');

console.log('🧪 Running tests for check_complexity.js...');

// Test 1: Error Propagation (Reproduction Case)
{
    console.log('   Test 1: Error Propagation (Reproduction Case)');
    const badNode = {
        toString: () => { throw new Error("Boom"); }
    };
    const nodeB = "B";

    const nodes = new Set([badNode, nodeB]);
    const edges = [
        { from: badNode, to: nodeB },
        { from: nodeB, to: badNode }
    ];

    try {
        calculateMaxDepth(nodes, edges);
        console.error("   ❌ FAIL: Error was swallowed! The function should have thrown 'Boom'.");
        process.exit(1);
    } catch (e) {
        if (e.message === "Boom") {
            console.log("   ✅ PASS: Error was propagated correctly!");
        } else {
            console.error("   ❌ FAIL: Wrong error thrown:", e);
            process.exit(1);
        }
    }
}

// Test 2: Happy Path (Depth Calculation)
{
    console.log('   Test 2: Happy Path (Depth Calculation)');
    const nodes = new Set(["A", "B", "C"]);
    const edges = [
        { from: "A", to: "B" },
        { from: "B", to: "C" }
    ];
    // A -> B -> C : Depth of A is 3 (A->B->C), B is 2 (B->C), C is 1. Max is 3.

    try {
        const depth = calculateMaxDepth(nodes, edges);
        if (depth === 3) {
            console.log(`   ✅ PASS: Depth calculated correctly: ${depth}`);
        } else {
            console.error(`   ❌ FAIL: Expected depth 3, got ${depth}`);
            process.exit(1);
        }
    } catch (e) {
        console.error("   ❌ FAIL: Unexpected error:", e);
        process.exit(1);
    }
}

// Test 3: Cycle Detection
{
    console.log('   Test 3: Cycle Detection');
    const nodes = new Set(["X", "Y"]);
    const edges = [
        { from: "X", to: "Y" },
        { from: "Y", to: "X" }
    ];

    try {
        calculateMaxDepth(nodes, edges);
        console.error("   ❌ FAIL: Cycle error was not thrown!");
        process.exit(1);
    } catch (e) {
        if (e.message.startsWith('Cycle detected')) {
            console.log("   ✅ PASS: Cycle detected correctly!");
        } else {
            console.error("   ❌ FAIL: Wrong error thrown for cycle:", e);
            process.exit(1);
        }
    }
}

// --- Tests for PR changes in check_complexity.js ---

// Test 4: cleanNodeId - simplified regex (PR change: dot no longer in pattern)
{
    console.log('   Test 4: cleanNodeId - basic alphanumeric and hyphen IDs');
    assert.strictEqual(cleanNodeId('MyNode'), 'MyNode', 'Basic alphanumeric ID should be extracted');
    assert.strictEqual(cleanNodeId('my_node'), 'my_node', 'Underscore should be preserved');
    assert.strictEqual(cleanNodeId('my-node'), 'my-node', 'Hyphen should be preserved');
    assert.strictEqual(cleanNodeId('NodeA[Label Text]'), 'NodeA', 'Should strip bracket labels');
    assert.strictEqual(cleanNodeId('NodeB("Text")'), 'NodeB', 'Should strip paren labels');
    assert.strictEqual(cleanNodeId(''), null, 'Empty string should return null');
    assert.strictEqual(cleanNodeId('   '), null, 'Whitespace-only should return null');
    console.log('   ✅ PASS: cleanNodeId handles all basic cases correctly');
}

// Test 5: cleanNodeId - dots no longer captured (PR simplified regex removes dot from pattern)
{
    console.log('   Test 5: cleanNodeId - dot is not part of node ID (simplified regex)');
    // Old regex: /^([a-zA-Z0-9_\-\.]+)/ — dots were allowed
    // New regex: /^([a-zA-Z0-9_\-]+)/ — dots not allowed
    const result = cleanNodeId('node.sub');
    // Only 'node' should be captured (stops at dot)
    assert.strictEqual(result, 'node', `Expected 'node', got '${result}'`);
    console.log('   ✅ PASS: cleanNodeId stops at dot (simplified regex)');
}

// Test 6: parseMermaid - basic arrow (MERMAID_EDGE_RE new pattern)
{
    console.log('   Test 6: parseMermaid - basic --> arrow');
    const content = `
    A --> B
    `;
    const { nodes, edges } = parseMermaid(content);
    assert.ok(nodes.has('A'), 'Node A should be present');
    assert.ok(nodes.has('B'), 'Node B should be present');
    assert.strictEqual(edges.length, 1, 'Should have exactly one edge');
    assert.deepStrictEqual(edges[0], { from: 'A', to: 'B' }, 'Edge should go from A to B');
    console.log('   ✅ PASS: parseMermaid handles basic --> arrow');
}

// Test 7: parseMermaid - chained arrows produce consecutive edges (new processEdgeParts)
{
    console.log('   Test 7: parseMermaid - chained A --> B --> C produces two edges');
    const content = `
    A --> B --> C
    `;
    const { nodes, edges } = parseMermaid(content);
    assert.ok(nodes.has('A'), 'Node A should be present');
    assert.ok(nodes.has('B'), 'Node B should be present');
    assert.ok(nodes.has('C'), 'Node C should be present');
    assert.strictEqual(edges.length, 2, 'Should have two edges from chained arrows');
    const hasBtoC = edges.some(e => e.from === 'B' && e.to === 'C');
    assert.ok(hasBtoC, 'Edge B -> C should exist');
    console.log('   ✅ PASS: Chained edges produce correct pairs');
}

// Test 8: parseMermaid - dotted arrow -.->
{
    console.log('   Test 8: parseMermaid - dotted -.->> arrow');
    const content = `
    X -.-> Y
    `;
    const { nodes, edges } = parseMermaid(content);
    assert.ok(nodes.has('X'), 'Node X should be present');
    assert.ok(nodes.has('Y'), 'Node Y should be present');
    assert.strictEqual(edges.length, 1, 'Should have one edge');
    console.log('   ✅ PASS: parseMermaid handles dotted arrows');
}

// Test 9: parseMermaid - labeled edge (A -- Label --> B)
{
    console.log('   Test 9: parseMermaid - labeled edge A -- Label --> B');
    const content = `
    P -- SomeLabel --> Q
    `;
    const { nodes, edges } = parseMermaid(content);
    assert.ok(nodes.has('P'), 'Node P should be present');
    assert.ok(nodes.has('Q'), 'Node Q should be present');
    assert.strictEqual(edges.length, 1, 'Should have one edge');
    assert.deepStrictEqual(edges[0], { from: 'P', to: 'Q' }, 'Edge should go from P to Q');
    console.log('   ✅ PASS: parseMermaid handles labeled edges');
}

// Test 10: parseMermaid - === double equals arrow
{
    console.log('   Test 10: parseMermaid - thick ==F==> arrow');
    const content = `
    E ==F==> G
    `;
    const { nodes, edges } = parseMermaid(content);
    assert.ok(nodes.has('E'), 'Node E should be present');
    assert.ok(nodes.has('G'), 'Node G should be present');
    assert.strictEqual(edges.length, 1, 'Should have one edge');
    console.log('   ✅ PASS: parseMermaid handles thick arrows');
}

// Test 11: expandNodes - & syntax for multiple sources
{
    console.log('   Test 11: expandNodes - ampersand multi-node syntax');
    const result = expandNodes('A & B');
    assert.ok(result.includes('A'), 'Should include A');
    assert.ok(result.includes('B'), 'Should include B');
    assert.strictEqual(result.length, 2, 'Should return exactly 2 nodes');
    console.log('   ✅ PASS: expandNodes handles & syntax');
}

// Test 12: parseMermaid - skips comment lines (%%)
{
    console.log('   Test 12: parseMermaid - skips %% comment lines');
    const content = `
    %% This is a comment
    A --> B
    %% Another comment
    `;
    const { nodes, edges } = parseMermaid(content);
    assert.strictEqual(nodes.size, 2, 'Should have exactly 2 nodes (not comment text)');
    assert.strictEqual(edges.length, 1, 'Should have one edge');
    console.log('   ✅ PASS: parseMermaid skips comment lines');
}

console.log('\n✨ All tests passed!');
