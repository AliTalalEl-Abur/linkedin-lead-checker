#!/usr/bin/env sh
set -eu

pattern="local""host\|127.0.0.""1"
if grep -RIn --exclude-dir node_modules --exclude-dir .git --exclude-dir .next --exclude-dir .vercel --exclude-dir dist --exclude-dir build "$pattern" .; then
  echo "❌ Localhost references detected"
  exit 1
fi

echo "✅ No localhost references found"
