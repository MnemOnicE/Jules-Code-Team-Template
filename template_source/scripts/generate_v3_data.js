/**
 * scripts/generate_v3_data.js
 * * RUN WITH: node scripts/generate_v3_data.js
 * * DESCRIPTION:
 * This script scaffolds the 'Evidence Locker' required for the V3 Jules Template.
 * 1. Creates tests/benchmarks/speed_log.json (Evidence for Bolt)
 * 2. Creates tests/mocks/large_payload.json (Ammo for Scope)
 */

const fs = require('fs');
const path = require('path');

// --- CONFIGURATION ---
const PATHS = {
  benchmarks: path.join(__dirname, '../tests/benchmarks'),
  mocks: path.join(__dirname, '../tests/mocks')
};

// --- DATA GENERATORS ---

function generateSpeedLog() {
  return {
    timestamp: new Date().toISOString(),
    environment: "staging",
    metrics: {
      "time_to_interactive": { value: 350, unit: "ms", threshold: 100, status: "FAIL" },
      "login_render_time": { value: 420, unit: "ms", threshold: 200, status: "FAIL" },
      "main_bundle_size": { value: 850, unit: "kb", threshold: 500, status: "WARN" },
      "db_query_users_avg": { value: 120, unit: "ms", threshold: 50, status: "FAIL" }
    },
    notes: "Automated benchmark run. Critical degradation in login render detected."
  };
}

function generateLargePayload() {
  const items = [];
  // Generate ~1,000 items to create a ~500KB file (Complying with 1MB Limit)
  for (let i = 0; i < 1000; i++) {
    items.push({
      id: `user_${i}`,
      name: `User Number ${i}`,
      email: `user${i}@example.com`,
      roles: ["admin", "editor", "viewer", "billing", "support"],
      metadata: {
        last_login: new Date().toISOString(),
        preferences: { theme: "dark", notifications: true, newsletter: false },
        history: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
      }
    });
  }
  return {
    meta: { description: "Stress Test Payload for Scope", size_est: "500KB" },
    data: items
  };
}

// --- MAIN EXECUTION ---

function init() {
  console.log("🚀 Initializing V3 Data Generation...");

  // 1. Ensure Directories Exist
  Object.values(PATHS).forEach(dir => {
    if (!fs.existsSync(dir)) {
      console.log(`Creating directory: ${dir}`);
      fs.mkdirSync(dir, { recursive: true });
    }
  });

  // 2. Write Speed Log (Bolt's Evidence)
  const speedLog = generateSpeedLog();
  fs.writeFileSync(
    path.join(PATHS.benchmarks, 'speed_log.json'),
    JSON.stringify(speedLog, null, 2)
  );
  console.log("✅ Generated: tests/benchmarks/speed_log.json (Bolt is watching this)");

  // 3. Write Large Payload (Scope's Ammo)
  const payload = generateLargePayload();
  fs.writeFileSync(
    path.join(PATHS.mocks, 'large_payload.json'),
    JSON.stringify(payload, null, 2)
  );
  console.log("✅ Generated: tests/mocks/large_payload.json (Scope is ready to break things)");

  console.log("\n🎉 V3 Environment Ready. Run '/standup' to test the new architecture.");
}

init();
