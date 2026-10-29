// The publication audit includes local routes, fragment anchors, byte-identical
// figures/downloads, deployment-base confinement and the static-file allowlist.
if (!process.argv.includes('--dist')) process.argv.push('--dist');
await import('./check-content.mjs');
