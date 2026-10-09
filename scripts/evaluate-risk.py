import subprocess
import json

def evaluate_diff():
    diff_stat = subprocess.run("git diff dev --stat", shell=True, capture_output=True, text=True).stdout.strip()
    
    files_changed = len(diff_stat.splitlines())
    
    dev_risk = min(5, max(1, files_changed // 3 + 1))
    main_risk = min(5, dev_risk + 1)
    
    blast_radius = "HIGH" if files_changed > 10 else ("MEDIUM" if files_changed > 4 else "LOW")
    revert_cost = "LOW"
    
    auto_merge_dev = (dev_risk <= 3) or (dev_risk == 4 and blast_radius == "LOW" and revert_cost == "LOW")
    
    result = {
        "dev_risk_score": dev_risk,
        "main_risk_score": main_risk,
        "blast_radius": blast_radius,
        "revert_cost": revert_cost,
        "auto_merge_dev_allowed": auto_merge_dev
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    evaluate_diff()
