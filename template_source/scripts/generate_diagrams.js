const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT_DIR, 'docs', 'diagrams');

// Ensure output directory exists
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

/**
 * Recursively scans directories for .mmd files, excluding specific paths.
 * Excludes: node_modules, .git, ingests, and tests/mocks.
 */
function getAllMermaidFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // General Exclusions
      if (file === 'node_modules' || file === '.git' || file === 'ingests') return;

      // Specific Exclusion: tests/mocks
      // We exclude any directory ending in 'tests/mocks'
      if (filePath.endsWith(path.join('tests', 'mocks'))) return;

      getAllMermaidFiles(filePath, fileList);
    } else {
      if (path.extname(file) === '.mmd') {
        fileList.push(filePath);
      }
    }
  });

  return fileList;
}

const files = getAllMermaidFiles(ROOT_DIR);
console.log(`📊 Generating Architecture Diagrams for ${files.length} files...`);

// Using local node_modules binary.
// Note: On Windows, this might require appending '.cmd' or using 'npx'.
// Assuming *nix environment for this template generator.
const mmdcPath = path.join(ROOT_DIR, 'node_modules', '.bin', 'mmdc');

// Track generated filenames to detect collisions
const usedNames = new Map(); // filename -> originalPath

files.forEach((file, index) => {
  const baseName = path.basename(file, '.mmd');
  let finalName = baseName;

  // Collision handling: append parent dir name if collision occurs
  if (usedNames.has(finalName)) {
    const parentDir = path.basename(path.dirname(file));
    finalName = `${parentDir}_${baseName}`;
    console.warn(`⚠️  Naming collision for '${baseName}'. Renaming to '${finalName}' to avoid overwriting.`);
  }

  usedNames.set(finalName, file);

  const pngOut = path.join(OUT_DIR, `${finalName}.png`);
  const svgOut = path.join(OUT_DIR, `${finalName}.svg`);

  console.log(`[${index + 1}/${files.length}] Processing ${baseName} -> ${finalName}...`);

  try {
    // Generate PNG
    execSync(`"${mmdcPath}" -i "${file}" -o "${pngOut}"`, { stdio: 'inherit', cwd: ROOT_DIR });
    // Generate SVG
    execSync(`"${mmdcPath}" -i "${file}" -o "${svgOut}"`, { stdio: 'inherit', cwd: ROOT_DIR });
  } catch (err) {
    console.error(`❌ Failed to generate diagrams for ${file}`);
    // We continue processing other diagrams even if one fails
  }
});

console.log(`✅ Diagrams generated in ${OUT_DIR}`);
