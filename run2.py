import subprocess

# subprocess.run(["python", "batch_extract_ipm_candidates.py"], check=True)
# subprocess.run(["python", "generate_embed_plan.py"], check=True)

subprocess.run(["python", "Cencoder2.py"], check=True)
subprocess.run(["python", "StegoDecoder2.py"], check=True)

