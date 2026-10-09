import subprocess
import os
import argparse

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def analyze(target_branch):
    os.makedirs(os.path.join(".agent-guard", "logs"), exist_ok=True)
    
    run_cmd(f"git fetch origin {target_branch}")
    base_hash = run_cmd(f"git merge-base HEAD origin/{target_branch}")
    local_hash = run_cmd("git rev-parse HEAD")
    upstream_hash = run_cmd(f"git rev-parse origin/{target_branch}")
    
    local_files = set(run_cmd(f"git diff --name-only {base_hash} HEAD").splitlines())
    upstream_files = set(run_cmd(f"git diff --name-only {base_hash} origin/{target_branch}").splitlines())
    
    overlapping = list(local_files.intersection(upstream_files))
    
    report = f"""# Upstream Pull Reconciliation Analysis

## Synchronization Metadata
- Local HEAD: `{local_hash[:7]}`
- Upstream (`origin/{target_branch}`): `{upstream_hash[:7]}`
- Common Ancestor Base: `{base_hash[:7]}`

## Divergence Metrics
- Local Modified Files: {len(local_files)}
- Upstream Modified Files: {len(upstream_files)}
- **Overlapping/Conflicting Files:** {len(overlapping)}

## Overlapping File Paths
"""
    if overlapping:
        for f in overlapping:
            report += f"- ⚠️ `{f}` (Requires agent reconciliation pass)\n"
    else:
        report += "No file overlaps detected. Clean rebase/merge expected.\n"
        
    log_path = os.path.join(".agent-guard", "logs", "LAST_PULL_ANALYSIS.md")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Analysis written to {log_path} | Overlaps: {len(overlapping)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="dev", help="Target branch to analyze")
    args = parser.parse_args()
    analyze(args.target)