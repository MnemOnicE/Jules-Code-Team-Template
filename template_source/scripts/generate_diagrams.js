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

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

/**
 * Sanitizes a filename to prevent it from being interpreted as a command-line flag.
 * Strips any leading hyphens.
 *
 * @param {string} name - The filename to sanitize.
 * @returns {string} The sanitized filename.
 */
function sanitizeFilename(name) {
  return name.replace(/^-+/, '');
}

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

function run() {
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
    let finalName = sanitizeFilename(baseName);

    // Collision handling: append parent dir name if collision occurs, then append counter if needed
    if (usedNames.has(finalName)) {
      const parentDir = path.basename(path.dirname(file));
      finalName = sanitizeFilename(`${parentDir}_${baseName}`);

      let counter = 1;
      const collisionBase = finalName;
      while (usedNames.has(finalName)) {
        finalName = `${collisionBase}_${counter++}`;
      }
      console.warn(`⚠️  Naming collision for '${baseName}'. Renaming to '${finalName}' to avoid overwriting.`);
    }

    usedNames.set(finalName, file);

    const pngOut = path.join(OUT_DIR, `${finalName}.png`);
    const svgOut = path.join(OUT_DIR, `${finalName}.svg`);

    console.log(`[${index + 1}/${files.length}] Processing ${baseName} -> ${finalName}...`);

    try {
      // Generate PNG
      // Using path.resolve to ensure paths are absolute, preventing argument injection.
      execFileSync(path.resolve(mmdcPath), ['-i', path.resolve(file), '-o', path.resolve(pngOut)], { stdio: 'inherit', cwd: ROOT_DIR });
      // Generate SVG
      execFileSync(path.resolve(mmdcPath), ['-i', path.resolve(file), '-o', path.resolve(svgOut)], { stdio: 'inherit', cwd: ROOT_DIR });
    } catch (err) {
      console.error(`❌ Failed to generate diagrams for ${file}`);
      // We continue processing other diagrams even if one fails
    }
  });

  console.log(`✅ Diagrams generated in ${OUT_DIR}`);
}

if (require.main === module) {
  run();
}

module.exports = {
  sanitizeFilename,
  getAllMermaidFiles,
  run
};
