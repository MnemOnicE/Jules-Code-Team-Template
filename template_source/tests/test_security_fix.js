const assert = require('assert');
const { sanitizeFilename } = require('../scripts/generate_diagrams');

console.log('🧪 Running Security Fix Tests for generate_diagrams.js...');

// Test 1: Regular filename
assert.strictEqual(sanitizeFilename('architecture'), 'architecture');
console.log('✅ Pass: Regular filename preserved');

// Test 2: Leading hyphen
assert.strictEqual(sanitizeFilename('-architecture'), 'architecture');
console.log('✅ Pass: Leading hyphen removed');

// Test 3: Multiple leading hyphens
assert.strictEqual(sanitizeFilename('--architecture'), 'architecture');
console.log('✅ Pass: Multiple leading hyphens removed');

// Test 4: Hyphen in the middle
assert.strictEqual(sanitizeFilename('my-architecture'), 'my-architecture');
console.log('✅ Pass: Middle hyphen preserved');

// Test 5: Empty string
assert.strictEqual(sanitizeFilename(''), '');
console.log('✅ Pass: Empty string handled');

console.log('\n🧪 Running Collision Robustness Simulation...');
// Simulating the collision logic in a testable way
function resolveCollision(baseName, parentDir, usedNames) {
  let finalName = sanitizeFilename(baseName);
  if (usedNames.has(finalName)) {
    finalName = sanitizeFilename(`${parentDir}_${baseName}`);
    let counter = 1;
    const collisionBase = finalName;
    while (usedNames.has(finalName)) {
      finalName = `${collisionBase}_${counter++}`;
    }
  }
  return finalName;
}

const used = new Set(['arch', 'docs_arch', 'docs_arch_1']);
assert.strictEqual(resolveCollision('arch', 'docs', used), 'docs_arch_2');
console.log('✅ Pass: Robust collision resolution handled multiple collisions');

console.log('🎉 All Tests Passed!');
