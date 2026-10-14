import subprocess,sys
for script in ["validate_reviews.py","analyze_reviews.py","generate_deliverables.py"]:
 print("\n>>>",script,flush=True)
 result=subprocess.run([sys.executable,script])
 if result.returncode: raise SystemExit(result.returncode)
print("\nDone. Review all files in outputs before approval.")
