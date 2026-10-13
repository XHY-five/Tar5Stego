import os
import subprocess

# 更改代码页为 UTF-8（适用于 Windows）
os.system('chcp 65001')

# 路径设置
hm_decoder = r".\Decoder\TAppDecoder.exe"  # HM 解码器路径
bitstream_dir = r"480p/results_bin/0.3_32_steg"  # 编码后的结果根目录（包含多个子目录，每个视频一个）
output_root = r".\480p\results\dec_steg_0.3_32"  # 解码输出根目录

# 创建输出根目录
os.makedirs(output_root, exist_ok=True)
iframe_log_path = os.path.join(output_root,'iframe_log.txt')
iframe_log = open(iframe_log_path,'w',encoding='utf-8')
# 检查路径是否存在
print(f"检查 HM 解码器路径：{hm_decoder}")
assert os.path.exists(hm_decoder), "HM 解码器路径不存在"

print(f"检查码流输入目录路径：{bitstream_dir}")
assert os.path.exists(bitstream_dir), "码流输入目录路径不存在"

# 遍历每个子目录（每个视频一个文件夹）
for name in os.listdir(bitstream_dir):
    video_dir = os.path.join(bitstream_dir, name)
    if not os.path.isdir(video_dir):
        continue

    # 找到 .bin 文件
    bin_files = [f for f in os.listdir(video_dir) if f.endswith(".265") or f.endswith(".bin")]
    if not bin_files:
        print(f"⚠️ 跳过：{name}，未找到 265/bin 文件")
        continue

    bitstream_path = os.path.join(video_dir, bin_files[0])

    # 解码输出目录
    video_outdir = os.path.join(output_root, name)
    if os.path.exists(video_outdir):
        print(f"⏩ 已完成：{video_outdir}，跳过 {name}")
        continue
    os.makedirs(video_outdir, exist_ok=True)

    output_yuv = os.path.join(video_outdir, f"{name}_steg_rec.yuv")
    output_ipm_steg_txt = os.path.join(video_outdir, f"{name}_steg_ipm.txt")
    output_coeff_steg_txt = os.path.join(video_outdir, f"{name}_steg_coeff.txt")

    # 构建解码命令
    cmd = (
        f'"{hm_decoder}" '
        f'-b "{bitstream_path}" '
        # f'-o "{output_yuv}" '
        f'--KeyInt=4 '
        f'--OutputIPMFile="{output_ipm_steg_txt}" '
        f'--OutputCoeffFile="{output_coeff_steg_txt}"'
    )

    print(f"🚀 开始解码：{bitstream_path}")
    print(f"执行的命令：\n{cmd}")

    # 执行命令
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        iframe_count=0
        # 实时输出日志
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line, end='')
            if '( I-SLICE' in line:
                iframe_count += 1
        process.wait()

        if process.returncode == 0:
            print(f"✅ 解码完成：{name}，输出保存在：{video_outdir}\n")
            # print(f"✅ 解码完成：{name}，输出保存在：{video_outdir}\n")

            iframe_log.write(f"{name},解码I帧总数：{iframe_count}帧\n\n")
        else:
            print(f"❌ 解码失败：{name}，错误代码：{process.returncode}\n")

    except Exception as e:
        print(f"❌ 解码过程中出错：{name}，错误信息：{str(e)}\n")

iframe_log.close()