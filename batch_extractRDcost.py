import os
import subprocess

# 设置编码页面为 UTF-8（可选）
os.system('chcp 65001')

# 配置路径
x265_encoder = r".\extractRDcostEncoder\x265.exe"
input_root = r"E:\xhy\testvideo480p"
output_cover_root = r".\480p\results_bin\32_covers"
input_coverinfo_root= r"E:\xhy\Tar3Data\480p\0.5_32\dec_ori_0.5_32"
output_root=r".\480p\results_rdcost\results_32_rdcost"
# 创建输出目录
os.makedirs(output_root, exist_ok=True)
os.makedirs(output_cover_root, exist_ok=True)
# 路径校验
assert os.path.exists(x265_encoder), "❌ x265 编码器路径不存在"
assert os.path.exists(input_root), "❌ 输入目录不存在"
qp=35
# 遍历所有子目录和 YUV 文件
for subdir in os.listdir(input_root):
    subdir_path = os.path.join(input_root, subdir)
    if not os.path.isdir(subdir_path):
        continue

    for file in os.listdir(subdir_path):
        if not file.endswith(".yuv"):
            continue

        yuv_path = os.path.join(subdir_path, file)
        base_name = os.path.splitext(file)[0]

        try:
            parts = base_name.split("_")
            name = parts[0]
            resolution = parts[1]
            fps = int(parts[2])
            segment_id = parts[-1][-3:]
            short_name = f"{name}segment{segment_id}"
            width, height = map(int, resolution.split("x"))
        except Exception as e:
            print(f"❌ 跳过无法解析命名的视频：{file}")
            continue

        # 输出路径设置
        video_outdir = os.path.join(output_root, short_name)
        video_output_cover_root= os.path.join(output_cover_root, short_name)
        video_input_coverinfo_root= os.path.join(input_coverinfo_root, short_name)
        os.makedirs(video_outdir, exist_ok=True)
        os.makedirs(video_output_cover_root, exist_ok=True)

        output_bitstream = os.path.join(video_output_cover_root, f"{short_name}_cover.265")
        cover_matchfile = os.path.join(video_input_coverinfo_root, f"{short_name}_cover_IPM.txt")
        output_candfile = os.path.join(video_outdir, f"{short_name}_ipm_cover_rdcost.txt")

        # 获取帧数（可自定义固定帧数）
        file_size = os.path.getsize(yuv_path)
        frame_size = int(width * height * 1.5)
        total_frames = int(file_size / frame_size)
        frame_num = 60

        # 构造 x265 命令
        cmd = (
            f'"{x265_encoder}" '
            f'-p 5 --frame-threads 1 '
            f'--input "{yuv_path}" --input-res {width}x{height} --fps {fps} '
            f'--output "{output_bitstream}" --profile main '
            f'--frames {frame_num} --keyint 4 --no-scenecut --b-adapt 0 --bframes 0 --qp {qp} '
            f'--input-matchfile "{cover_matchfile}" '
            f'--output-candidate "{output_candfile}"'
        )

        print(f"\n🚀 正在处理：{file}")
        print(f"▶ 命令：{cmd}\n")

        try:
            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8'
            )
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print(line, end='')

            process.wait()
            if process.returncode == 0:
                print(f"✅ 完成：{file}，输出在 {video_outdir}")
            else:
                print(f"❌ 编码失败：{file}，错误码 {process.returncode}")

        except Exception as e:
            print(f"❌ 执行异常：{file}，错误：{e}")
