const assert = require('assert');
const { calculateMaxDepth } = require('../scripts/check_complexity');

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

console.log('\n✨ All tests passed!');
