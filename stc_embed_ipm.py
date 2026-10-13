# # import numpy as np
# # import json
# # import subprocess
# # import argparse
# # import os
# #
# # # === 解析命令行参数 ===
# # parser = argparse.ArgumentParser()
# # parser.add_argument("--embedding_plan", type=str, required=True, help="输入 embedding_plan.json 路径")
# # parser.add_argument("--output_txt", type=str, required=True, help="输出 stego_IPM.txt 文件")
# # parser.add_argument("--payload", type=int, default=None, help="嵌入的总比特数（优先级高于 embed_ratio）")
# # parser.add_argument("--embed_ratio", type=float, default=1.0, help="嵌入比例（0-1）")
# # parser.add_argument("--constraint_height", type=int, default=7, help="STC 高度 h")
# # parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe", help="STC 可执行文件路径")
# # parser.add_argument("--seed", type=int, default=42)
# # args = parser.parse_args()
# #
# # # === 临时 STC 输入文件 ===
# # COVER_BIN = "cover.dat"
# # RHO_BIN = "rho.dat"
# # MESSAGE_BIN = "message.dat"
# # STEGO_BIN = "stego.dat"
# #
# # # === 读取 embedding_plan.json ===
# # with open(args.embedding_plan, "r") as f:
# #     plan = json.load(f)
# #
# # plan = sorted(plan, key=lambda x: x["id"])
# #
# # # 构造 cover / rho
# # cover = np.array([p["ori"] for p in plan], dtype=np.uint8)
# # rho = np.full((len(plan), 3), np.inf, dtype=np.float32)
# # for i, p in enumerate(plan):
# #     ori, alt, r = p["ori"], p["alt"], p["rho"]
# #     rho[i, 1] = 0
# #     if alt == ori - 1:
# #         rho[i, 0] = r
# #     elif alt == ori + 1:
# #         rho[i, 2] = r
# #
# # # 生成消息 bits
# # n = len(plan)
# # if args.payload is not None:
# #     message_len = min(args.payload, n)
# # else:
# #     message_len = int(n * args.embed_ratio)
# # np.random.seed(args.seed)
# # message = np.random.randint(0, 2, size=message_len).astype(np.uint8)
# #
# # # 写入 STC 输入文件
# # cover.tofile(COVER_BIN)
# # rho.tofile(RHO_BIN)
# # message.tofile(MESSAGE_BIN)
# #
# # # 调用 STC
# # subprocess.run([
# #     args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(args.constraint_height)
# # ], check=True)
# #
# # # 读取 stego bits
# # stego = np.fromfile(STEGO_BIN, dtype=np.uint8)[:message_len]
# #
# # # 推断帧号
# # frame_id = 1
# # for token in os.path.basename(args.embedding_plan).split("_"):
# #     if token.isdigit():
# #         frame_id = int(token)
# #         break
# #
# # # 写入输出 txt（含 rho_d, rho_s）
# # with open(args.output_txt, "w") as f:
# #     f.write(f"Frame {frame_id} begin\n")
# #     for i in range(message_len):
# #         p = plan[i]
# #         ori, alt = p["ori"], p["alt"]
# #         steg_ipm = alt if stego[i] else ori
# #         ctu = p.get("ctu", -1)
# #         rho = p.get("rho", 0.0)
# #         rho_s = p.get("rho_s", 0.0)
# #         rho_d = p.get("rho_d", 0.0)
# #         f.write(f"CTU Address: {ctu} x={p['x']},y={p['y']} paritionSize=3 depth=3 size=8x8 "
# #                 f"oriIPM={ori} stegIPM={steg_ipm} rho={rho:.2f} rho_s={rho_s:.2f} rho_d={rho_d:.2f}\n")
# #     f.write(f"Frame {frame_id} end\n")
# #
# # print(f"✅ 嵌入完成：{message_len} bits，结果已保存至 {args.output_txt}")
# #
# #
# #
# # import os
# # import json
# # import glob
# # import numpy as np
# # import subprocess
# # import argparse
# # import re
# # from collections import defaultdict
# #
# # # === 参数 ===
# # parser = argparse.ArgumentParser()
# # parser.add_argument("--cover_ipm", type=str, required=True, help="cover_ipm.txt 作为基底")
# # parser.add_argument("--embedding_plan_dir", type=str, required=True, help="embedding_plan 所在目录（frame_*.json）")
# # parser.add_argument("--output_txt", type=str, required=True, help="输出 stego_ipm.txt")
# # parser.add_argument("--payload", type=int, default=None)
# # parser.add_argument("--embed_ratio", type=float, default=1.0)
# # parser.add_argument("--constraint_height", type=int, default=7)
# # parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe")
# # parser.add_argument("--seed", type=int, default=42)
# # args = parser.parse_args()
# #
# # # === 临时 STC 文件 ===
# # COVER_BIN, RHO_BIN, MESSAGE_BIN, STEGO_BIN = "cover.dat", "rho.dat", "message.dat", "stego.dat"
# #
# # def write_bin(fname, array, dtype=np.uint8):
# #     np.array(array, dtype=dtype).tofile(fname)
# #
# # # === Step1: 加载所有 embedding_plan.json ===
# # plan_files = sorted(glob.glob(os.path.join(args.embedding_plan_dir, "frame_*_embedding_plan.json")))
# # print(f"找到 {len(plan_files)} 个 embedding_plan")
# #
# # # === Step2: 逐帧跑 STC，得到修改的 4x4 PU ===
# # np.random.seed(args.seed)
# # stego_map = {}  # key=(frame,ctu,x,y) → new_ipm
# #
# # for plan_path in plan_files:
# #     frame_id = int(re.search(r"frame_(\d+)_embedding_plan\.json", os.path.basename(plan_path)).group(1))
# #     with open(plan_path, "r") as f:
# #         plan = json.load(f)
# #     plan = sorted(plan, key=lambda x: x["id"])
# #
# #     # 构造 cover / rho
# #     cover = np.array([p["ori"] for p in plan], dtype=np.uint8)
# #     rho = np.full((len(plan), 3), np.inf, dtype=np.float32)
# #     for i, p in enumerate(plan):
# #         ori, alt, r = p["ori"], p["alt"], p["rho"]
# #         rho[i, 1] = 0
# #         if alt == ori - 1:
# #             rho[i, 0] = r
# #         elif alt == ori + 1:
# #             rho[i, 2] = r
# #
# #     # 消息
# #     n = len(plan)
# #     if args.payload is not None:
# #         message_len = min(args.payload, n)
# #     else:
# #         message_len = int(n * args.embed_ratio)
# #     message = np.random.randint(0, 2, size=message_len).astype(np.uint8)
# #
# #     # 写 STC 输入
# #     write_bin(COVER_BIN, cover)
# #     write_bin(RHO_BIN, rho, dtype=np.float32)
# #     write_bin(MESSAGE_BIN, message)
# #
# #     subprocess.run([args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(args.constraint_height)], check=True)
# #     stego_bits = np.fromfile(STEGO_BIN, dtype=np.uint8)[:message_len]
# #
# #     # 更新 stego_map
# #     for i in range(message_len):
# #         p = plan[i]
# #         steg_ipm = p["alt"] if stego_bits[i] else p["ori"]
# #         stego_map[(frame_id, p.get("ctu", -1), p["x"], p["y"])] = steg_ipm
# #
# # print(f"STC 嵌入完成，共修改 {len(stego_map)} 个 4×4 PU")
# #
# # # === Step3: 遍历 cover_ipm.txt，替换 4x4 PU ===
# # pattern_cover = re.compile(
# #     r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)"
# # )
# # output_lines = []
# # current_frame = None
# # with open(args.cover_ipm, "r") as f:
# #     for line in f:
# #         line = line.strip()
# #         if line.startswith("Frame") and "begin" in line:
# #             current_frame = int(line.split()[1])
# #             output_lines.append(line + "\n")
# #             continue
# #         if "end" in line:
# #             output_lines.append(line + "\n")
# #             current_frame = None
# #             continue
# #
# #         m = pattern_cover.search(line)
# #         if not m:
# #             output_lines.append(line + "\n")
# #             continue
# #
# #         ctu, x, y, partsize, depth, size, ipm = m.groups()
# #         ctu, x, y, partsize, depth, ipm = int(ctu), int(x), int(y), int(partsize), int(depth), int(ipm)
# #         new_ipm = ipm
# #         if partsize == 3 and depth == 3 and size == "8x8":  # 仅替换 4x4
# #             new_ipm = stego_map.get((current_frame, ctu, x, y), ipm)
# #
# #         output_lines.append(
# #             f"CTU Address: {ctu} x={x},y={y} paritionSize={partsize} depth={depth} size={size} IPM={new_ipm}\n"
# #         )
# #
# # # === Step4: 写出 stego_ipm.txt ===
# # with open(args.output_txt, "w") as f:
# #     f.writelines(output_lines)
# #
# # print(f"✅ 完成：生成 {args.output_txt}")
# import os
# import json
# import glob
# import numpy as np
# import subprocess
# import argparse
# import re
# from collections import defaultdict
#
# # === 参数 ===
# parser = argparse.ArgumentParser()
# parser.add_argument("--cover_ipm", type=str, required=True, help="cover_ipm.txt 作为基底")
# parser.add_argument("--embedding_plan_dir", type=str, required=True, help="embedding_plan 所在目录（frame_*.json）")
# parser.add_argument("--output_txt", type=str, required=True, help="输出 stego_ipm.txt")
# parser.add_argument("--payload", type=int, default=None)
# parser.add_argument("--embed_ratio", type=float, default=1.0)
# parser.add_argument("--constraint_height", type=int, default=7)
# parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe")
# parser.add_argument("--seed", type=int, default=42)
# args = parser.parse_args()
#
# # === 临时 STC 文件 ===
# COVER_BIN, RHO_BIN, MESSAGE_BIN, STEGO_BIN = "cover.dat", "rho.dat", "message.dat", "stego.dat"
#
# def write_bin(fname, array, dtype=np.uint8):
#     np.array(array, dtype=dtype).tofile(fname)
#
# # === Step1: 加载所有 embedding_plan.json ===
# plan_files = sorted(glob.glob(os.path.join(args.embedding_plan_dir, "frame_*_embedding_plan.json")))
# print(f"找到 {len(plan_files)} 个 embedding_plan")
#
# # === Step2: 逐帧跑 STC，得到修改的 4x4 PU ===
# np.random.seed(args.seed)
# stego_map = {}  # key=(frame,ctu,x,y) → (ori_ipm, steg_ipm)
#
# for plan_path in plan_files:
#     frame_id = int(re.search(r"frame_(\d+)_embedding_plan\.json", os.path.basename(plan_path)).group(1))
#     with open(plan_path, "r") as f:
#         plan = json.load(f)
#     plan = sorted(plan, key=lambda x: x["id"])
#
#     # 构造 cover / rho
#     cover = np.array([p["ori"] for p in plan], dtype=np.uint8)
#     rho = np.full((len(plan), 3), np.inf, dtype=np.float32)
#     for i, p in enumerate(plan):
#         ori, alt, r = p["ori"], p["alt"], p["rho"]
#         rho[i, 1] = 0
#         if alt == ori - 1:
#             rho[i, 0] = r
#         elif alt == ori + 1:
#             rho[i, 2] = r
#
#     # 消息
#     n = len(plan)
#     if args.payload is not None:
#         message_len = min(args.payload, n)
#     else:
#         message_len = int(n * args.embed_ratio)
#     message = np.random.randint(0, 2, size=message_len).astype(np.uint8)
#
#     # 写 STC 输入
#     write_bin(COVER_BIN, cover)
#     write_bin(RHO_BIN, rho, dtype=np.float32)
#     write_bin(MESSAGE_BIN, message)
#
#     subprocess.run([args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(args.constraint_height)], check=True)
#     stego_bits = np.fromfile(STEGO_BIN, dtype=np.uint8)[:message_len]
#
#     # 更新 stego_map
#     for i in range(message_len):
#         p = plan[i]
#         steg_ipm = p["alt"] if stego_bits[i] else p["ori"]
#         stego_map[(frame_id, p.get("ctu", -1), p["x"], p["y"])] = (p["ori"], steg_ipm)
#
# print(f"STC 嵌入完成，共修改 {len(stego_map)} 个 4×4 PU")
#
# # === Step3: 遍历 cover_ipm.txt，替换 4x4 PU，输出 ori+steg ===
# pattern_cover = re.compile(
#     r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)"
# )
# output_lines = []
# current_frame = None
# with open(args.cover_ipm, "r") as f:
#     for line in f:
#         line = line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1])
#             output_lines.append(line + "\n")
#             continue
#         if "end" in line:
#             output_lines.append(line + "\n")
#             current_frame = None
#             continue
#
#         m = pattern_cover.search(line)
#         if not m:
#             output_lines.append(line + "\n")
#             continue
#
#         ctu, x, y, partsize, depth, size, ipm = m.groups()
#         ctu, x, y, partsize, depth, ipm = int(ctu), int(x), int(y), int(partsize), int(depth), int(ipm)
#         ori_ipm, steg_ipm = ipm, ipm
#         if partsize == 3 and depth == 3 and size == "8x8":  # 仅替换 4x4
#             ori_ipm, steg_ipm = stego_map.get((current_frame, ctu, x, y), (ipm, ipm))
#
#         output_lines.append(
#             f"CTU Address: {ctu} x={x},y={y} paritionSize={partsize} depth={depth} size={size} oriIPM={ori_ipm} stegIPM={steg_ipm}\n"
#         )
#
# # === Step4: 写出 stego_ipm.txt ===
# with open(args.output_txt, "w") as f:
#     f.writelines(output_lines)
#
# print(f"✅ 完成：生成 {args.output_txt}")
# import os, json, glob, numpy as np, subprocess, argparse, re
# from collections import defaultdict
#
# # === 参数 ===
# parser = argparse.ArgumentParser()
# parser.add_argument("--cover_ipm", type=str, required=True, help="cover_ipm.txt 作为基底")
# parser.add_argument("--embedding_plan_dir", type=str, required=True, help="embedding_plan 所在目录（frame_*.json）")
# parser.add_argument("--output_txt", type=str, required=True, help="输出 stego_ipm.txt")
# parser.add_argument("--payload", type=int, default=None, help="总嵌入比特（优先级高于 ratio）")
# parser.add_argument("--frame_payload_ratio", type=float, default=None, help="按每帧 4×4 块数量的比例嵌入")
# parser.add_argument("--embed_ratio", type=float, default=1.0, help="按 embedding_plan 长度比例嵌入（旧参数）")
# parser.add_argument("--constraint_height", type=int, default=7)
# parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe")
# parser.add_argument("--seed", type=int, default=42)
# args = parser.parse_args()
#
# # === 临时 STC 文件 ===
# COVER_BIN, RHO_BIN, MESSAGE_BIN, STEGO_BIN = "cover.dat", "rho.dat", "message.dat", "stego.dat"
# def write_bin(fname, array, dtype=np.uint8):
#     np.array(array, dtype=dtype).tofile(fname)
#
# # === 读取 cover_ipm（统计每帧 4×4 PU 数）===
# frame_4x4_count = defaultdict(int)
# pattern_cover_line = re.compile(
#     r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)"
# )
# current_frame = None
# with open(args.cover_ipm,'r') as f:
#     for line in f:
#         line=line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1]); continue
#         if "end" in line:
#             current_frame = None; continue
#         m = pattern_cover_line.search(line)
#         if m and current_frame is not None:
#             partsize, depth, size = int(m.group(4)), int(m.group(5)), m.group(6)
#             if partsize == 3 and depth == 3 and size == "8x8":
#                 frame_4x4_count[current_frame] += 1
#
# # === 加载所有 embedding_plan.json ===
# plan_files = sorted(glob.glob(os.path.join(args.embedding_plan_dir, "frame_*_embedding_plan.json")))
# print(f"找到 {len(plan_files)} 个 embedding_plan")
#
# np.random.seed(args.seed)
# stego_map = {}  # key=(frame,ctu,x,y) → new_ipm
#
# # === 逐帧跑 STC ===
# for plan_path in plan_files:
#     frame_id = int(re.search(r"frame_(\d+)_embedding_plan\.json", os.path.basename(plan_path)).group(1))
#     with open(plan_path, "r") as f:
#         plan = json.load(f)
#     plan = sorted(plan, key=lambda x: x["rho"])  # 按代价升序
#
#     # === 确定嵌入数量 ===
#     if args.payload is not None:
#         message_len = min(args.payload, len(plan))
#     elif args.frame_payload_ratio is not None:
#         total_4x4 = frame_4x4_count.get(frame_id, len(plan))
#         message_len = min(int(total_4x4 * args.frame_payload_ratio), len(plan))
#     else:
#         message_len = int(len(plan) * args.embed_ratio)
#     plan = plan[:message_len]  # 只取前 message_len 个
#
#     # 构造 cover / rho
#     cover = np.array([p["ori"] for p in plan], dtype=np.uint8)
#     rho = np.full((len(plan), 3), np.inf, dtype=np.float32)
#     for i, p in enumerate(plan):
#         ori, alt, r = p["ori"], p["alt"], p["rho"]
#         rho[i, 1] = 0
#         if alt == ori - 1:
#             rho[i, 0] = r
#         elif alt == ori + 1:
#             rho[i, 2] = r
#
#     # 消息
#     message = np.random.randint(0, 2, size=len(plan)).astype(np.uint8)
#
#     # 写 STC 输入
#     write_bin(COVER_BIN, cover)
#     write_bin(RHO_BIN, rho, dtype=np.float32)
#     write_bin(MESSAGE_BIN, message)
#     subprocess.run([args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(args.constraint_height)], check=True)
#     stego_bits = np.fromfile(STEGO_BIN, dtype=np.uint8)[:len(plan)]
#
#     # 更新 stego_map
#     for i in range(len(plan)):
#         p = plan[i]
#         steg_ipm = p["alt"] if stego_bits[i] else p["ori"]
#         stego_map[(frame_id, p.get("ctu", -1), p["x"], p["y"])] = steg_ipm
#
# print(f"STC embedding finished. Modified blocks: {len(stego_map)}")
#
# # === 遍历 cover_ipm.txt，替换 4x4 PU ===
# output_lines = []
# current_frame = None
# with open(args.cover_ipm, "r") as f:
#     for line in f:
#         line = line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1])
#             output_lines.append(line + "\n")
#             continue
#         if "end" in line:
#             output_lines.append(line + "\n")
#             current_frame = None
#             continue
#
#         m = pattern_cover_line.search(line)
#         if not m:
#             output_lines.append(line + "\n")
#             continue
#
#         ctu, x, y, partsize, depth, size, ipm = m.groups()
#         ctu, x, y, partsize, depth, ipm = int(ctu), int(x), int(y), int(partsize), int(depth), int(ipm)
#         new_ipm = stego_map.get((current_frame, ctu, x, y), ipm)
#         output_lines.append(
#             f"CTU Address: {ctu} x={x},y={y} paritionSize={partsize} depth={depth} size={size} oriIPM={ipm} stegIPM={new_ipm}\n"
#         )
#
# with open(args.output_txt, "w") as f:
#     f.writelines(output_lines)
#
# print(f"✅ 完成：生成 {args.output_txt}")
# import os, json, glob, numpy as np, subprocess, argparse, re
# from collections import defaultdict
#
# # === 参数 ===
# parser = argparse.ArgumentParser()
# parser.add_argument("--cover_ipm", type=str, required=True)
# parser.add_argument("--embedding_plan_dir", type=str, required=True)
# parser.add_argument("--output_txt", type=str, required=True)
# parser.add_argument("--payload", type=int, default=None)
# parser.add_argument("--frame_payload_ratio", type=float, default=None)
# parser.add_argument("--embed_ratio", type=float, default=1.0)
# parser.add_argument("--constraint_height", type=int, default=7)
# parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe")
# parser.add_argument("--seed", type=int, default=42)
# parser.add_argument("--eta", type=float, default=8.0)
# args = parser.parse_args()
#
# # === 临时 STC 文件 ===
# COVER_BIN, RHO_BIN, MESSAGE_BIN, STEGO_BIN = "cover.dat", "rho.dat", "message.dat", "stego.dat"
# def write_bin(fname, array, dtype=np.uint8):
#     np.array(array, dtype=dtype).tofile(fname)
#
# # === 读取 cover_ipm（统计每帧 4×4 PU 数）===
# frame_4x4_count = defaultdict(int)
# pattern_cover_line = re.compile(r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)")
# with open(args.cover_ipm,'r') as f:
#     current_frame = None
#     for line in f:
#         line=line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1]); continue
#         if "end" in line:
#             current_frame = None; continue
#         m = pattern_cover_line.search(line)
#         if m and current_frame is not None:
#             partsize, depth, size = int(m.group(4)), int(m.group(5)), m.group(6)
#             if partsize == 3 and depth == 3 and size == "8x8":
#                 frame_4x4_count[current_frame] += 1
#
# # === UpDist（轻量） ===
# def apply_updist(plan, selected_ids, eta=8.0):
#     selected_positions = {(p["x"], p["y"]) for p in plan if p["id"] in selected_ids}
#     for p in plan:
#         if (p["x"], p["y"]) in selected_positions: continue
#         if any(abs(p["x"] - sx) < 8 and abs(p["y"] - sy) < 8 for sx, sy in selected_positions):
#             p["rho"] = p["rho"] / eta
#
# # === 分层推进选择 ===
# def select_with_layer_updist(plan, message_len, eta=8.0):
#     layers = defaultdict(list)
#     for p in plan:
#         layers[p.get("layer_id", 0)].append(p)
#     selected, selected_ids = [], set()
#     for lid in sorted(layers.keys()):
#         batch = sorted(layers[lid], key=lambda x: x["rho"])
#         for p in batch:
#             if len(selected) >= message_len: break
#             selected.append(p)
#             selected_ids.add(p["id"])
#         apply_updist(plan, selected_ids, eta=eta)
#         if len(selected) >= message_len: break
#     return selected
#
# # === 加载所有 embedding_plan.json ===
# plan_files = sorted(glob.glob(os.path.join(args.embedding_plan_dir, "frame_*_embedding_plan.json")))
# print(f"找到 {len(plan_files)} 个 embedding_plan")
#
# np.random.seed(args.seed)
# stego_map = {}
#
# # === 逐帧跑 STC ===
# for plan_path in plan_files:
#     frame_id = int(re.search(r"frame_(\d+)_embedding_plan\.json", os.path.basename(plan_path)).group(1))
#     with open(plan_path, "r") as f:
#         plan = json.load(f)
#     # 确定嵌入数量
#     if args.payload is not None:
#         message_len = min(args.payload, len(plan))
#     elif args.frame_payload_ratio is not None:
#         total_4x4 = frame_4x4_count.get(frame_id, len(plan))
#         message_len = min(int(total_4x4 * args.frame_payload_ratio), len(plan))
#     else:
#         message_len = int(len(plan) * args.embed_ratio)
#     # 分层推进选择
#     plan = select_with_layer_updist(plan, message_len, eta=args.eta)
#
#     cover = np.array([p["ori"] for p in plan], dtype=np.uint8)
#     rho = np.full((len(plan), 3), np.inf, dtype=np.float32)
#     for i, p in enumerate(plan):
#         ori, alt, r = p["ori"], p["alt"], p["rho"]
#         rho[i, 1] = 0
#         if alt == ori - 1: rho[i, 0] = r
#         elif alt == ori + 1: rho[i, 2] = r
#
#     message = np.random.randint(0, 2, size=len(plan)).astype(np.uint8)
#     write_bin(COVER_BIN, cover); write_bin(RHO_BIN, rho, dtype=np.float32); write_bin(MESSAGE_BIN, message)
#     subprocess.run([args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(args.constraint_height)], check=True)
#     stego_bits = np.fromfile(STEGO_BIN, dtype=np.uint8)[:len(plan)]
#     for i in range(len(plan)):
#         p = plan[i]
#         steg_ipm = p["alt"] if stego_bits[i] else p["ori"]
#         stego_map[(frame_id, p.get("ctu", -1), p["x"], p["y"])] = steg_ipm
#
# print(f"STC embedding finished. Modified blocks: {len(stego_map)}")
#
# # === 遍历 cover_ipm.txt，替换 4x4 PU ===
# output_lines, current_frame = [], None
# with open(args.cover_ipm, "r") as f:
#     for line in f:
#         line = line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1]); output_lines.append(line + "\n"); continue
#         if "end" in line:
#             output_lines.append(line + "\n"); current_frame = None; continue
#         m = pattern_cover_line.search(line)
#         if not m: output_lines.append(line + "\n"); continue
#         ctu, x, y, partsize, depth, size, ipm = m.groups()
#         ctu, x, y, partsize, depth, ipm = int(ctu), int(x), int(y), int(partsize), int(depth), int(ipm)
#         new_ipm = stego_map.get((current_frame, ctu, x, y), ipm)
#         output_lines.append(f"CTU Address: {ctu} x={x},y={y} paritionSize={partsize} depth={depth} size={size} oriIPM={ipm} stegIPM={new_ipm}\n")
# with open(args.output_txt, "w") as f:
#     f.writelines(output_lines)
# print(f"✅ 完成：生成 {args.output_txt}")
# import os, json, glob, numpy as np, subprocess, argparse, re
# from collections import defaultdict
#
# # === 参数 ===
# parser = argparse.ArgumentParser()
# parser.add_argument("--cover_ipm", type=str, required=True)
# parser.add_argument("--embedding_plan_dir", type=str, required=True)
# parser.add_argument("--output_txt", type=str, required=True)
# parser.add_argument("--payload", type=int, default=None)
# parser.add_argument("--frame_payload_ratio", type=float, default=None)
# parser.add_argument("--embed_ratio", type=float, default=1.0)
# parser.add_argument("--constraint_height", type=int, default=7)
# parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe")
# parser.add_argument("--seed", type=int, default=42)
# parser.add_argument("--eta", type=float, default=8.0)
# args = parser.parse_args()
#
# COVER_BIN, RHO_BIN, MESSAGE_BIN, STEGO_BIN = "cover.dat", "rho.dat", "message.dat", "stego.dat"
# def write_bin(fname, array, dtype=np.uint8):
#     np.array(array, dtype=dtype).tofile(fname)
#
# # === 读取 cover_ipm（统计每帧 4×4 PU 数）===
# frame_4x4_count = defaultdict(int)
# pattern_cover_line = re.compile(r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)")
# with open(args.cover_ipm,'r') as f:
#     current_frame = None
#     for line in f:
#         line=line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1]); continue
#         if "end" in line:
#             current_frame = None; continue
#         m = pattern_cover_line.search(line)
#         if m and current_frame is not None:
#             partsize, depth, size = int(m.group(4)), int(m.group(5)), m.group(6)
#             if partsize == 3 and depth == 3 and size == "8x8":
#                 frame_4x4_count[current_frame] += 1
#
# # === UpDist（轻量） ===
# def apply_updist(plan, selected_ids, eta=8.0):
#     selected_positions = {(p["x"], p["y"]) for p in plan if p["id"] in selected_ids}
#     for p in plan:
#         if (p["x"], p["y"]) in selected_positions: continue
#         if any(abs(p["x"] - sx) < 8 and abs(p["y"] - sy) < 8 for sx, sy in selected_positions):
#             p["rho"] = p["rho"] / eta
#
# # === 分层推进选择 ===
# def select_with_layer_updist(plan, message_len, eta=8.0):
#     layers = defaultdict(list)
#     for p in plan:
#         layers[p.get("layer_id", 0)].append(p)
#     selected, selected_ids = [], set()
#     for lid in sorted(layers.keys()):
#         batch = sorted(layers[lid], key=lambda x: x["rho"])
#         for p in batch:
#             if len(selected) >= message_len: break
#             selected.append(p)
#             selected_ids.add(p["id"])
#         apply_updist(plan, selected_ids, eta=eta)
#         if len(selected) >= message_len: break
#     return selected
#
# # === 加载所有 embedding_plan.json ===
# plan_files = sorted(glob.glob(os.path.join(args.embedding_plan_dir, "frame_*_embedding_plan.json")))
# print(f"找到 {len(plan_files)} 个 embedding_plan")
#
# np.random.seed(args.seed)
# stego_map = {}
# global_total_candidates = 0
# global_total_embedded = 0
#
# # === 逐帧跑 STC ===
# for plan_path in plan_files:
#     frame_id = int(re.search(r"frame_(\d+)_embedding_plan\.json", os.path.basename(plan_path)).group(1))
#     with open(plan_path, "r") as f:
#         plan = json.load(f)
#
#     # === 统计候选数 ===
#     total_candidates = len(plan)
#     global_total_candidates += total_candidates
#
#     # === 确定嵌入数量 ===
#     if args.payload is not None:
#         message_len = min(args.payload, total_candidates)
#     elif args.frame_payload_ratio is not None:
#         total_4x4 = frame_4x4_count.get(frame_id, total_candidates)
#         message_len = min(int(total_4x4 * args.frame_payload_ratio), total_candidates)
#     else:
#         message_len = int(total_candidates * args.embed_ratio)
#
#     # === 分层推进选择 ===
#     plan = select_with_layer_updist(plan, message_len, eta=args.eta)
#     global_total_embedded += len(plan)
#
#     # === 打印统计 ===
#     print(f"[Frame {frame_id}] candidates={total_candidates}, selected={len(plan)}, ratio={len(plan)/total_candidates:.2%}")
#
#     # === 构造 cover / rho ===
#     cover = np.array([p["ori"] for p in plan], dtype=np.uint8)
#     rho = np.full((len(plan), 3), np.inf, dtype=np.float32)
#     for i, p in enumerate(plan):
#         ori, alt, r = p["ori"], p["alt"], p["rho"]
#         rho[i, 1] = 0
#         if alt == ori - 1: rho[i, 0] = r
#         elif alt == ori + 1: rho[i, 2] = r
#
#     message = np.random.randint(0, 2, size=len(plan)).astype(np.uint8)
#     write_bin(COVER_BIN, cover); write_bin(RHO_BIN, rho, dtype=np.float32); write_bin(MESSAGE_BIN, message)
#     subprocess.run([args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(args.constraint_height)], check=True)
#     stego_bits = np.fromfile(STEGO_BIN, dtype=np.uint8)[:len(plan)]
#     for i in range(len(plan)):
#         p = plan[i]
#         steg_ipm = p["alt"] if stego_bits[i] else p["ori"]
#         stego_map[(frame_id, p.get("ctu", -1), p["x"], p["y"])] = steg_ipm
#
# print(f"\nSTC embedding finished.")
# print(f"Global: {global_total_embedded}/{global_total_candidates} ({global_total_embedded/global_total_candidates:.2%}) blocks embedded.")
#
# # === 遍历 cover_ipm.txt，替换 4x4 PU ===
# output_lines, current_frame = [], None
# with open(args.cover_ipm, "r") as f:
#     for line in f:
#         line = line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1]); output_lines.append(line + "\n"); continue
#         if "end" in line:
#             output_lines.append(line + "\n"); current_frame = None; continue
#         m = pattern_cover_line.search(line)
#         if not m: output_lines.append(line + "\n"); continue
#         ctu, x, y, partsize, depth, size, ipm = m.groups()
#         ctu, x, y, partsize, depth, ipm = int(ctu), int(x), int(y), int(partsize), int(depth), int(ipm)
#         new_ipm = stego_map.get((current_frame, ctu, x, y), ipm)
#         output_lines.append(f"CTU Address: {ctu} x={x},y={y} paritionSize={partsize} depth={depth} size={size} oriIPM={ipm} stegIPM={new_ipm}\n")
# with open(args.output_txt, "w") as f:
#     f.writelines(output_lines)
# print(f"✅ 完成：生成 {args.output_txt}")
# import os, json, glob, numpy as np, subprocess, argparse, re, time
# from collections import defaultdict
#
# # === 参数 ===
# parser = argparse.ArgumentParser()
# parser.add_argument("--cover_ipm", type=str, required=True)
# parser.add_argument("--embedding_plan_dir", type=str, required=True)
# parser.add_argument("--output_txt", type=str, required=True)
# parser.add_argument("--payload", type=int, default=None)
# parser.add_argument("--frame_payload_ratio", type=float, default=None)
# parser.add_argument("--embed_ratio", type=float, default=1.0)
# parser.add_argument("--constraint_height", type=int, default=7)
# parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe")
# parser.add_argument("--seed", type=int, default=42)
# parser.add_argument("--eta", type=float, default=8.0)
# parser.add_argument("--batch_step", type=int, default=6, help="每批推进的层数")
# args = parser.parse_args()
#
# # === 临时 STC 文件 ===
# COVER_BIN, RHO_BIN, MESSAGE_BIN, STEGO_BIN = "cover.dat", "rho.dat", "message.dat", "stego.dat"
# def write_bin(fname, array, dtype=np.uint8):
#     np.array(array, dtype=dtype).tofile(fname)
#
# # === 读取 cover_ipm（统计每帧 4×4 PU 数）===
# frame_4x4_count = defaultdict(int)
# pattern_cover_line = re.compile(r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)")
# with open(args.cover_ipm,'r') as f:
#     current_frame = None
#     for line in f:
#         line=line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1]); continue
#         if "end" in line:
#             current_frame = None; continue
#         m = pattern_cover_line.search(line)
#         if m and current_frame is not None:
#             partsize, depth, size = int(m.group(4)), int(m.group(5)), m.group(6)
#             if partsize == 3 and depth == 3 and size == "8x8":
#                 frame_4x4_count[current_frame] += 1
#
# # === UpDist 优化：用 8×8 网格索引，只更新邻居桶 ===
# def build_spatial_index(plan):
#     grid = defaultdict(list)
#     for idx, p in enumerate(plan):
#         gx, gy = p["x"] // 8, p["y"] // 8
#         grid[(gx, gy)].append(idx)
#     return grid
#
#
# # 新增空间分区选择函数
# def select_by_spatial_grid(batch, target):
#     grid = defaultdict(list)
#     for p in batch:
#         # 将帧划分为8x8网格
#         grid_x, grid_y = p["x"] // 64, p["y"] // 64  # 假设CTU=64x64
#         grid[(grid_x, grid_y)].append(p)
#
#     selected = []
#     per_grid_target = max(1, target // len(grid))
#
#     for cell in grid.values():
#         # 每个网格单元内按失真排序
#         cell_sorted = sorted(cell, key=lambda x: x["rho"])
#         selected.extend(cell_sorted[:per_grid_target])
#         if len(selected) >= target:
#             break
#     return selected[:target]
#
# def apply_updist(plan, selected_ids, grid, eta=8.0):
#     selected_coords = {(p["x"] // 8, p["y"] // 8) for p in plan if p["id"] in selected_ids}
#     visited = set()
#     for cx, cy in selected_coords:
#         for nx in range(cx-1, cx+2):
#             for ny in range(cy-1, cy+2):
#                 if (nx, ny) not in grid or (nx, ny) in visited:
#                     continue
#                 visited.add((nx, ny))
#                 for idx in grid[(nx, ny)]:
#                     p = plan[idx]
#                     if p["id"] in selected_ids:
#                         continue
#                     p["rho"] = p["rho"] / eta
#
# # === 多层批量推进选择 ===
# def select_with_layer_updist(plan, message_len, eta=8.0, step=6):
#     """多层推进选择 + UpDist优化 + 空间均衡"""
#     # 按层分组
#     layers = defaultdict(list)
#     for p in plan:
#         layers[p.get("layer_id", 0)].append(p)
#
#     # 准备空间索引（用于UpDist）
#     grid = build_spatial_index(plan)
#
#     # 随机化层处理顺序（关键改进）
#     layer_ids = sorted(layers.keys())
#     np.random.shuffle(layer_ids)
#
#     # 计算空间网格配额
#     grid_quota = {}
#     if plan:  # 避免空计划
#         # 获取最大坐标
#         max_x = max(p["x"] for p in plan) + 8
#         max_y = max(p["y"] for p in plan) + 8
#         grid_cols = max(1, max_x // 64)
#         grid_rows = max(1, max_y // 64)
#         total_grids = grid_cols * grid_rows
#
#         # 基础配额 + 右下角补偿
#         base_quota = max(1, message_len // total_grids)
#         for gy in range(grid_rows):
#             for gx in range(grid_cols):
#                 # 右下角权重更高 (1.0-1.5)
#                 position_bias = 1.0 + (gx / grid_cols + gy / grid_rows) * 0.5
#                 grid_quota[(gx, gy)] = int(base_quota * position_bias)
#
#     selected, selected_ids = [], set()
#
#     # 按随机层顺序处理
#     for lid in layer_ids:
#         # 打乱当前层内顺序
#         np.random.shuffle(layers[lid])
#
#         for p in layers[lid]:
#             if len(selected) >= message_len:
#                 break
#
#             # 空间配额检查
#             gx, gy = p["x"] // 64, p["y"] // 64
#             grid_key = (gx, gy)
#
#             if grid_quota.get(grid_key, 0) > 0:
#                 selected.append(p)
#                 selected_ids.add(p["id"])
#                 grid_quota[grid_key] -= 1
#
#         # 应用UpDist优化
#         apply_updist(plan, selected_ids, grid, eta=eta)
#
#         # 每处理step层后检查
#         if lid % step == 0 and len(selected) >= message_len:
#             break
#
#     # 如果配额未用完，补充选择
#     if len(selected) < message_len:
#         remaining = [p for p in plan if p["id"] not in selected_ids]
#         np.random.shuffle(remaining)
#         selected.extend(remaining[:message_len - len(selected)])
#
#     return selected
#
# # === 加载所有 embedding_plan.json ===
# plan_files = sorted(glob.glob(os.path.join(args.embedding_plan_dir, "frame_*_embedding_plan.json")))
# print(f"找到 {len(plan_files)} 个 embedding_plan")
#
# np.random.seed(args.seed)
# stego_map = {}
# global_total_candidates = 0
# global_total_embedded = 0
#
# # === 逐帧跑 STC ===
# for plan_path in plan_files:
#     frame_id = int(re.search(r"frame_(\d+)_embedding_plan\.json", os.path.basename(plan_path)).group(1))
#     with open(plan_path, "r") as f:
#         plan = json.load(f)
#
#     total_candidates = len(plan)
#     global_total_candidates += total_candidates
#
#     # 确定嵌入数量
#     if args.payload is not None:
#         message_len = min(args.payload, total_candidates)
#     elif args.frame_payload_ratio is not None:
#         total_4x4 = frame_4x4_count.get(frame_id, total_candidates)
#         message_len = min(int(total_4x4 * args.frame_payload_ratio), total_candidates)
#     else:
#         message_len = int(total_candidates * args.embed_ratio)
#
#     print(f"[Frame {frame_id}] candidates={total_candidates}, target={message_len}")
#
#     # 分层推进选择 + UpDist（批量推进）
#     start_upd = time.time()
#     plan = select_with_layer_updist(plan, message_len, eta=args.eta, step=args.batch_step)
#     print(f"    [Frame {frame_id}] Batch step={args.batch_step}, UpDist time: {time.time()-start_upd:.3f}s")
#
#     global_total_embedded += len(plan)
#
#     # === 构造 cover / rho ===
#     cover = np.array([p["ori"] for p in plan], dtype=np.uint8)
#     rho = np.full((len(plan), 3), np.inf, dtype=np.float32)
#     for i, p in enumerate(plan):
#         ori, alt, r = p["ori"], p["alt"], p["rho"]
#         rho[i, 1] = 0
#         if alt == ori - 1: rho[i, 0] = r
#         elif alt == ori + 1: rho[i, 2] = r
#
#     message = np.random.randint(0, 2, size=len(plan)).astype(np.uint8)
#     write_bin(COVER_BIN, cover); write_bin(RHO_BIN, rho, dtype=np.float32); write_bin(MESSAGE_BIN, message)
#     subprocess.run([args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(args.constraint_height)], check=True)
#     stego_bits = np.fromfile(STEGO_BIN, dtype=np.uint8)[:len(plan)]
#     for i in range(len(plan)):
#         p = plan[i]
#         steg_ipm = p["alt"] if stego_bits[i] else p["ori"]
#         stego_map[(frame_id, p.get("ctu", -1), p["x"], p["y"])] = steg_ipm
#
# print(f"\nSTC embedding finished.")
# if global_total_candidates > 0:
#     ratio = global_total_embedded / global_total_candidates
# else:
#     ratio = 0
# print(f"Global: {global_total_embedded}/{global_total_candidates} ({ratio:.2%}) blocks embedded.")
#
# # === 解析 cover_ipm.txt 为块列表 ===
# cover_blocks = []
# pattern_line = re.compile(r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)")
# current_frame = None
# with open(args.cover_ipm, 'r') as f:
#     for line in f:
#         line = line.strip()
#         if line.startswith("Frame") and "begin" in line:
#             current_frame = int(line.split()[1])
#             continue
#         if "end" in line:
#             current_frame = None
#             continue
#         m = pattern_line.search(line)
#         if not m:
#             continue
#         ctu, x, y, partsize, depth, size, ipm = m.groups()
#         cover_blocks.append((current_frame, int(ctu), int(x), int(y), int(partsize), int(depth), size, int(ipm)))
#
# # === Step4: 生成 C文件（保留 A 结构，仅修改 4×4 PU） ===
# modified_map = stego_map  # 与 Tar4 对齐变量名
# modified_count=0
# with open(args.output_txt, 'w') as f:
#     current_frame = None
#     for block in cover_blocks:
#         frame, ctu, x, y, partsize, depth, size, ori = block
#         if frame != current_frame:
#             if current_frame is not None:
#                 f.write(f"Frame {current_frame} end\n")
#             current_frame = frame
#             f.write(f"Frame {frame} begin\n")
#         steg = ori
#         if partsize == 3 and depth == 3 and size == "8x8":
#             steg = modified_map.get((frame, ctu, x, y), ori)
#             if steg!=ori:
#                 modified_count+=1
#         f.write(f"CTU Address: {ctu} x={x},y={y} paritionSize={partsize} depth={depth} size={size} oriIPM={ori} stegIPM={steg}\n")
#     if current_frame is not None:
#         f.write(f"Frame {current_frame} end\n")
#
# print(f"\n✅ 嵌入IPM总数：{len(modified_map)} 修改IPM数：{modified_count}, 输出文件: {args.output_txt}")
import os, json, glob, numpy as np, subprocess, argparse, re, time
from collections import defaultdict

# === 参数 ===
parser = argparse.ArgumentParser()
parser.add_argument("--cover_ipm", type=str, required=True)
parser.add_argument("--embedding_plan_dir", type=str, required=True)
parser.add_argument("--output_txt", type=str, required=True)
parser.add_argument("--payload", type=int, default=None)
parser.add_argument("--frame_payload_ratio", type=float, default=None)
parser.add_argument("--embed_ratio", type=float, default=1.0)
parser.add_argument("--constraint_height", type=int, default=7)
parser.add_argument("--stc_exe", type=str, default="./stc/example1_ml_stc.exe")
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--eta", type=float, default=8.0)
parser.add_argument("--batch_step", type=int, default=6, help="每批推进的层数")
args = parser.parse_args()

# === 临时 STC 文件 ===
COVER_BIN, RHO_BIN, MESSAGE_BIN, STEGO_BIN = "cover.dat", "rho.dat", "message.dat", "stego.dat"


def write_bin(fname, array, dtype=np.uint8):
    np.array(array, dtype=dtype).tofile(fname)


# === 读取 cover_ipm（统计每帧 4×4 PU 数）===
frame_4x4_count = defaultdict(int)
pattern_cover_line = re.compile(
    r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)")
with open(args.cover_ipm, 'r') as f:
    current_frame = None
    for line in f:
        line = line.strip()
        if line.startswith("Frame") and "begin" in line:
            current_frame = int(line.split()[1]);
            continue
        if "end" in line:
            current_frame = None;
            continue
        m = pattern_cover_line.search(line)
        if m and current_frame is not None:
            partsize, depth, size = int(m.group(4)), int(m.group(5)), m.group(6)
            if partsize == 3 and depth == 3 and size == "8x8":
                frame_4x4_count[current_frame] += 1


# === UpDist 优化：用 8×8 网格索引，只更新邻居桶 ===
def build_spatial_index(plan):
    grid = defaultdict(list)
    for idx, p in enumerate(plan):
        gx, gy = p["x"] // 8, p["y"] // 8
        grid[(gx, gy)].append(idx)
    return grid


def apply_updist(plan, selected_ids, grid, eta=8.0):
    selected_coords = {(p["x"] // 8, p["y"] // 8) for p in plan if p["id"] in selected_ids}
    visited = set()
    for cx, cy in selected_coords:
        for nx in range(cx - 1, cx + 2):
            for ny in range(cy - 1, cy + 2):
                if (nx, ny) not in grid or (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                for idx in grid[(nx, ny)]:
                    p = plan[idx]
                    if p["id"] in selected_ids:
                        continue
                    # 确保失真值是有限的
                    if np.isfinite(p["rho"]):
                        p["rho"] = p["rho"] / eta
                    # else:
                    #     print(f"警告: 块 {p['id']} 有无效失真值: {p['rho']}, 使用默认值 100.0")
                    #     p["rho"] = 100.0


# === 多层STC嵌入（论文方法）===
def layered_stc_embedding(plan, message_len, constraint_height=7, eta=8.0, step=6):
    """
    完整实现论文分层 STC 嵌入流程（±1 IPM 替换），输入为 embedding_plan（含 ori、alt、rho、layer_id）
    - 加入容量检测：message_len > 有效候选数时直接截断
    - 加入 rho 清洗：替换 inf / nan / 负值
    """
    from collections import defaultdict
    import math

    # === 分层准备 ===
    layers = defaultdict(list)
    for p in plan:
        lid = p.get("layer_id", 0)
        layers[lid].append(p)

    sorted_lids = sorted(layers.keys())
    if not sorted_lids:
        print("❌ plan 中没有有效 layer_id")
        return []

    # === 合并 step 层一批 ===
    batches = []
    for i in range(0, len(sorted_lids), step):
        batch = []
        for lid in sorted_lids[i:i + step]:
            batch.extend(layers[lid])
        batches.append(batch)

    grid = build_spatial_index(plan)
    selected, selected_ids = [], set()

    # === 预处理 rho（清洗无效值） ===
    for p in plan:
        if not np.isfinite(p["rho"]) or p["rho"] < 0:
            p["rho"] = 1e9  # 大代价，等效不可选

    # === 容量检测：计算可用候选数 ===
    valid_candidates = [p for p in plan if np.isfinite(p["rho"]) and p["rho"] < 1e8]
    if message_len > len(valid_candidates):
        print(f"⚠️ 嵌入容量不足: 请求 {message_len} bit, 可用 {len(valid_candidates)}，自动截断")
        message_len = len(valid_candidates)

    # === 分批嵌入 ===
    for bidx, batch in enumerate(batches):
        remain = message_len - len(selected)
        if remain <= 0:
            break

        batch = [p for p in batch if p["id"] not in selected_ids]
        batch = sorted(batch, key=lambda x: x["rho"])
        if not batch:
            continue

        N = min(remain, len(batch))
        message = np.random.randint(0, 2, size=N).astype(np.uint8)

        # 构造 STC cover / rho
        batch_sel = batch[:N]
        # 修改点：同时传递原始值和替代值
        cover_or_alt = []  # 交替存储 ori 和 alt
        for p in batch_sel:
            cover_or_alt.append(p["ori"])
            cover_or_alt.append(p["alt"])

        cover_or_alt = np.array(cover_or_alt, dtype=np.uint8)
        rho = np.array([p["rho"] for p in batch_sel], dtype=np.float32)
        rho[rho == 0] = 1e-6
        write_bin(COVER_BIN, cover_or_alt)
        write_bin(RHO_BIN, rho, dtype=np.float32)
        write_bin(MESSAGE_BIN, message)
        try:
            subprocess.run(
                [args.stc_exe, COVER_BIN, MESSAGE_BIN, RHO_BIN, STEGO_BIN, str(constraint_height)],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ [LayerGroup {bidx}] STC 嵌入失败: {e}")
            break

        stego_bits = np.fromfile(STEGO_BIN, dtype=np.uint8)[:N]

        for i in range(N):
            p = dict(batch[i])
            p["steg_ipm"] = p["alt"] if stego_bits[i] == 1 else p["ori"]
            selected.append(p)
            selected_ids.add(p["id"])

        if any(stego_bits):
            apply_updist(plan, selected_ids, grid, eta=eta)

    print(f"✅ 最终嵌入：{len(selected)} 个块")
    return selected

# === 加载所有 embedding_plan.json ===
plan_files = sorted(glob.glob(os.path.join(args.embedding_plan_dir, "frame_*_embedding_plan.json")))
print(f"找到 {len(plan_files)} 个 embedding_plan")

np.random.seed(args.seed)
stego_map = {}
global_total_candidates = 0
global_total_embedded = 0
global_total = 0
# === 逐帧跑 STC ===
for plan_path in plan_files:
    frame_id = int(re.search(r"frame_(\d+)_embedding_plan\.json", os.path.basename(plan_path)).group(1))
    print(f"加载嵌入计划: {plan_path}")

    plan = []  # 初始化为空列表

    with open(plan_path, "r") as f:
        try:
            plan_data = json.load(f)
            # print(f"  加载的数据类型: {type(plan_data)}")

            # 检查是字典还是列表
            if isinstance(plan_data, dict):
                # 如果包含 "plan" 键，则提取嵌入计划
                if "plan" in plan_data:
                    plan = plan_data["plan"]
                    # print(f"  从字典中提取嵌入计划，计划长度: {len(plan)}")
                else:
                    print(f"  错误: 字典中缺少 'plan' 键")
                    continue
            elif isinstance(plan_data, list):
                plan = plan_data
                # print(f"  直接加载列表格式嵌入计划，长度: {len(plan)}")
            else:
                print(f"  错误: 未知的嵌入计划格式: {type(plan_data)}")
                continue

            # 调试: 检查第一个元素的类型
            if plan and len(plan) > 0:
                first_item = plan[0]
                # print(f"  第一个元素类型: {type(first_item)}, 内容: {str(first_item)[:50]}...")

                # 检查失真值是否有效
                if "rho" in first_item and not np.isfinite(first_item["rho"]):
                    print(f"  警告: 第一个块有无效失真值: {first_item['rho']}")
        except Exception as e:
            print(f"加载JSON失败: {e}")
            continue

    # 如果提取失败，跳过当前帧
    if not plan or not isinstance(plan, list):
        print(f"  错误: 无效的嵌入计划格式")
        continue

    total_candidates = len(plan)
    global_total_candidates += total_candidates
    global_total += frame_4x4_count.get(frame_id, total_candidates)
    # 确定嵌入数量
    if args.payload is not None:
        message_len = min(args.payload, total_candidates)
    elif args.frame_payload_ratio is not None:
        total_4x4 = frame_4x4_count.get(frame_id, total_candidates)
        message_len = min(int(total_4x4 * args.frame_payload_ratio), total_candidates)
    else:
        message_len = int(total_candidates * args.embed_ratio)

    print(f"[Frame {frame_id}] candidates={total_candidates}, target={message_len}")

    # 分层STC嵌入
    start_upd = time.time()
    try:
        selected_blocks = layered_stc_embedding(
            plan,
            message_len,
            constraint_height=args.constraint_height,
            eta=args.eta,
            step=args.batch_step
        )
    except Exception as e:
        print(f"分层STC嵌入失败: {e}")
        continue

    # 更新全局计数
    num_embedded = len(selected_blocks) if selected_blocks else 0
    global_total_embedded += num_embedded
    print(f"    [Frame {frame_id}] STC time: {time.time() - start_upd:.3f}s, embedded: {num_embedded} blocks")

    # 记录修改结果
    for p in selected_blocks:
        if isinstance(p, dict) and "x" in p and "y" in p:
            ctu = p.get("ctu", -1)
            stego_map[(frame_id, ctu, p["x"], p["y"])] = p["steg_ipm"]
        else:
            print(f"警告: 无效的块数据: {p}")

print(f"\nSTC embedding finished.")
if global_total_candidates > 0:
    ratio = global_total_embedded / global_total_candidates
else:
    ratio = 0
if global_total > 0:
    ratio2 = global_total_embedded / global_total
else:
    ratio2=0
print(f"Global cand: {global_total_embedded}/{global_total_candidates} ({ratio:.2%}) blocks embedded. ")
print(f"Global : {global_total_embedded}/{global_total} ({ratio2:.2%}) blocks embedded. ")
# === 解析 cover_ipm.txt 为块列表 ===
cover_blocks = []
pattern_line = re.compile(
    r"CTU Address:\s*(\d+)\s+x=(\d+),y=(\d+)\s+paritionSize=(\d+)\s+depth=(\d+)\s+size=([0-9]+x[0-9]+)\s+IPM=(\d+)")
current_frame = None
with open(args.cover_ipm, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith("Frame") and "begin" in line:
            current_frame = int(line.split()[1])
            continue
        if "end" in line:
            current_frame = None
            continue
        m = pattern_line.search(line)
        if not m:
            continue
        ctu, x, y, partsize, depth, size, ipm = m.groups()
        cover_blocks.append((current_frame, int(ctu), int(x), int(y), int(partsize), int(depth), size, int(ipm)))

# === Step4: 生成 C文件（保留 A 结构，仅修改 4×4 PU） ===
modified_count = 0
with open(args.output_txt, 'w') as f:
    current_frame = None
    for block in cover_blocks:
        frame, ctu, x, y, partsize, depth, size, ori = block
        if frame != current_frame:
            if current_frame is not None:
                f.write(f"Frame {current_frame} end\n")
            current_frame = frame
            f.write(f"Frame {frame} begin\n")

        steg = ori
        if partsize == 3 and depth == 3 and size == "8x8":
            key = (frame, ctu, x, y)
            if key in stego_map:
                steg = stego_map[key]
                if steg != ori:
                    modified_count += 1

        f.write(
            f"CTU Address: {ctu} x={x},y={y} paritionSize={partsize} depth={depth} size={size} oriIPM={ori} stegIPM={steg}\n")

    if current_frame is not None:
        f.write(f"Frame {current_frame} end\n")

print(f"\n✅ 嵌入IPM总数：{global_total_embedded} 修改IPM数：{modified_count}, 输出文件: {args.output_txt}")