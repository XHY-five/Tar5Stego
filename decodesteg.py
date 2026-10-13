import os
import subprocess
import shutil

# === 基础配置 ===
os.system('chcp 65001')

hm_decoder = r".\decoder\TAppDecoder.exe"     # HM 解码器路径
input_base = r"E:\xhy\Tar5stego\results_bin"              # 输入根目录
temp_output_base = r".\dec_results"           # 临时输出目录
final_output_base = r"G:\xhy\AnalysisProject\tar5"  # 最终保存目录
keyint = 12                                   # GOP 间隔

qp_list = [24, 28, 32]
payload_list = [0.1, 0.3, 0.5]

# === 检查路径 ===
assert os.path.exists(hm_decoder), "❌ HM 解码器路径不存在"
assert os.path.exists(input_base), "❌ 输入根目录不存在"

# === 遍历每个 QP × payload ===
for qp in qp_list:
    for payload in payload_list:

        bitstream_dir = os.path.join(input_base, f"steg_{payload}_{qp}")
        temp_root = os.path.join(temp_output_base, f"dec_steg_{payload}_{qp}")
        final_root = os.path.join(final_output_base, f"dec_steg_{payload}_{qp}")

        if not os.path.exists(bitstream_dir):
            print(f"⚠️ 跳过 QP={qp}, payload={payload}：未找到目录 {bitstream_dir}")
            continue

        os.makedirs(temp_root, exist_ok=True)
        os.makedirs(final_root, exist_ok=True)

        print(f"\n==================== 开始解码 QP={qp}, payload={payload} ====================")
        print(f"输入目录：{bitstream_dir}")
        print(f"输出目录：{temp_root}")

        # === 遍历每个视频文件夹 ===
        for name in os.listdir(bitstream_dir):
            video_dir = os.path.join(bitstream_dir, name)
            if not os.path.isdir(video_dir):
                continue

            # 查找码流文件
            bin_files = [f for f in os.listdir(video_dir) if f.endswith(".265") or f.endswith(".bin")]
            if not bin_files:
                print(f"⚠️ 跳过：{name}，未找到 265/bin 文件")
                continue

            bitstream_path = os.path.join(video_dir, bin_files[0])
            video_outdir = os.path.join(temp_root, name)

            # 若已存在则跳过
            if os.path.exists(os.path.join(final_root, name)):
                print(f"⏩ 已存在：{name}，跳过")
                continue

            os.makedirs(video_outdir, exist_ok=True)

            output_ipm_steg_txt = os.path.join(video_outdir, f"{name}_steg_ipm.txt")
            output_coeff_steg_txt = os.path.join(video_outdir, f"{name}_steg_coeff.txt")

            # 构建 HM 解码命令
            cmd = (
                f'"{hm_decoder}" '
                f'-b "{bitstream_path}" '
                f'--KeyInt={keyint} '
                f'--OutputIPMFile="{output_ipm_steg_txt}" '
                f'--OutputCoeffFile="{output_coeff_steg_txt}"'
            )

            print(f"\n🚀 开始解码：{bitstream_path}")
            print(f"▶ 命令：{cmd}")

            try:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8'
                )

                for line in process.stdout:
                    print(line, end='')

                process.wait()

                if process.returncode == 0:
                    print(f"✅ 解码完成：{name}")

                    # === 立即剪切当前视频段到最终目录 ===
                    dest_dir = os.path.join(final_root, name)
                    if os.path.exists(dest_dir):
                        shutil.rmtree(dest_dir)
                    shutil.move(video_outdir, dest_dir)

                    print(f"📦 已剪切到目标路径：{dest_dir}\n")

                else:
                    print(f"❌ 解码失败：{name}（错误代码 {process.returncode}）\n")

            except Exception as e:
                print(f"❌ 解码过程中出错：{name}，错误：{e}\n")

        print(f"✅ QP={qp}, payload={payload} 所有视频已处理完毕。\n")

print("\n🎯 所有 QP + payload 解码任务完成，结果已全部移动到目标目录！")
