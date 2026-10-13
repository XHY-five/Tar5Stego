# import os
# import subprocess
# import glob
#
# # ==== 配置参数 ====
# embedding_plan_root = r"./utils/0.3_32_embedding_plan"  # B
# cover_root = r"E:\xhy\test\Tar3AnalysisProject\dec_ori_0.3_32"                 # A
# output_root = r"./Tar5stegresults/0.3_32_steg"          # C
# stc_embed_script = "stc_embed_ipm.py"
# stc_exe_path = r"./stc/example1_ml_stc.exe"
# embed_ratio = 0.3
# constraint_height = 7
# seed = 42
# payload = None  # 可设为整数，如 2000
#
# # ==== 遍历每个 segment ====
# seg_dirs = glob.glob(f"{embedding_plan_root}/**/", recursive=True)
# seg_dirs = [d for d in seg_dirs if os.path.isdir(d) and "frame_" in "".join(os.listdir(d))]
#
# for seg_dir in seg_dirs:
#     seg_name = os.path.basename(os.path.normpath(seg_dir))
#
#     # === 找 cover 文件（同名） ===
#     cover_dir = os.path.join(cover_root, seg_name)
#     cover_ipm_file = os.path.join(cover_dir, f"{seg_name}_cover_ipm.txt")
#     if not os.path.exists(cover_ipm_file):
#         print(f"❌ 未找到 cover 文件：{cover_ipm_file}，跳过 {seg_name}")
#         continue
#
#     out_dir = os.path.join(output_root, seg_name)
#     os.makedirs(out_dir, exist_ok=True)
#     merged_output_txt = os.path.join(out_dir, f"{seg_name}_stego_IPM.txt")
#
#     # === 调用改造后的 stc_embed_ipm.py，直接生成完整 stego_ipm ===
#     cmd = [
#         "python", stc_embed_script,
#         "--cover_ipm", cover_ipm_file,
#         "--embedding_plan_dir", seg_dir,
#         "--output_txt", merged_output_txt,
#         "--embed_ratio", str(embed_ratio),
#         "--constraint_height", str(constraint_height),
#         "--stc_exe", stc_exe_path,
#         "--seed", str(seed)
#     ]
#     if payload is not None:
#         cmd.extend(["--payload", str(payload)])
#
#     print(f"\n🚀 正在处理 Segment：{seg_name}")
#     print("▶ 命令：", " ".join(cmd))
#     subprocess.run(cmd, check=True)
#
#     print(f"📦 完成：{merged_output_txt}")
#
# print("\n✅ 所有 STC 嵌入完成，输出目录：", output_root)
import os, subprocess, glob

# ==== 配置参数 ====
embedding_plan_root = r"./480p/utils/32_embedding_plan"  # B
cover_root = r"E:\xhy\Tar3Data\480p\0.5_32\dec_ori_0.5_32"  # A
output_root = r"./Tar5stegresults/480p/32_steg"  # C
stc_embed_script = "stc_embed_ipm.py"
stc_exe_path = r"./stc/example1_ml_stc.exe"
payload_ratios = [0.1,0.3,0.5]  # 多 payload
constraint_height = 7
seed = 42

seg_dirs = glob.glob(f"{embedding_plan_root}/**/", recursive=True)
seg_dirs = [d for d in seg_dirs if os.path.isdir(d) and "frame_" in "".join(os.listdir(d))]

for ratio in payload_ratios:
    print(f"\n===== 处理 payload={ratio} =====")
    out_dir_ratio = os.path.join(output_root, f"payload_{ratio}")
    os.makedirs(out_dir_ratio, exist_ok=True)

    for seg_dir in seg_dirs:
        seg_name = os.path.basename(os.path.normpath(seg_dir))
        cover_dir = os.path.join(cover_root, seg_name)
        cover_ipm_file = os.path.join(cover_dir, f"{seg_name}_cover_ipm.txt")
        if not os.path.exists(cover_ipm_file):
            print(f"❌ 未找到 cover 文件：{cover_ipm_file}，跳过 {seg_name}")
            continue

        out_dir = os.path.join(out_dir_ratio, seg_name)
        # === 跳过已完成的目录 ===
        if os.path.exists(out_dir):
            print(f"⏩ 已完成：{out_dir}，跳过 {seg_name}")
            continue
        os.makedirs(out_dir, exist_ok=True)
        merged_output_txt = os.path.join(out_dir, f"{seg_name}_stego_IPM.txt")

        cmd = [
            "python", stc_embed_script,
            "--cover_ipm", cover_ipm_file,
            "--embedding_plan_dir", seg_dir,
            "--output_txt", merged_output_txt,
            "--frame_payload_ratio", str(ratio),
            "--constraint_height", str(constraint_height),
            "--stc_exe", stc_exe_path,
            "--seed", str(seed)
        ]
        print(f"\n🚀 处理 Segment {seg_name} (payload={ratio})")
        subprocess.run(cmd, check=True)
        print(f"📦 完成：{merged_output_txt}")
