import fs from 'fs';
import path from 'path';

const searchDir = 'c:/Users/RUSHITHA/OneDrive/Desktop/NLP/trustlens';

function replaceInFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let newContent = content
    .replace(/TrustLens/g, 'TrustLens')
    .replace(/trustlens/g, 'trustlens')
    .replace(/TRUSTLENS/g, 'TRUSTLENS')
    .replace(/TrustLens/g, 'TrustLens');
    
  if (content !== newContent) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    console.log('Updated: ' + filePath);
  }
}

function walk(dir) {
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat && stat.isDirectory()) {
      if (!file.includes('node_modules') && !file.includes('.git') && !file.includes('dist')) {
        walk(filePath);
      }
    } else {
      const ext = path.extname(filePath);
      if (['.ts', '.tsx', '.html', '.js', '.json', '.yml', '.yaml'].includes(ext)) {
        replaceInFile(filePath);
      }
    }
  }
}

walk(searchDir);
console.log('Done.');
