import os
import subprocess

os.system('chcp 65001')

x265_encoder = r".\C_Coder\x265.exe"  # 替换为 x265 可执行文件路径
input_root = r"E:\xhy\testvideo480p"
output_root = r".\480p\results_bin\0.3_32_steg"
output_root2 = r".\Tar5stegresults\480p\32_steg\payload_0.3"

os.makedirs(output_root, exist_ok=True)
qp=35
print(f"检查 x265 编码器路径：{x265_encoder}")
assert os.path.exists(x265_encoder), "x265 编码器路径不存在"

print(f"检查输入目录路径：{input_root}")
assert os.path.exists(input_root), "输入目录路径不存在"

# 遍历 test_video 下所有子目录
for subdir in os.listdir(input_root):
    subdir_path = os.path.join(input_root, subdir)
    if not os.path.isdir(subdir_path):
        continue

    # 遍历子目录中的 .yuv 文件
    for file in os.listdir(subdir_path):
        if not file.endswith(".yuv"):
            continue

        base_name = os.path.splitext(file)[0]
        input_path = os.path.join(subdir_path, file)

        try:
            parts = base_name.split("_")
            name = parts[0]
            resolution = parts[1]
            fps = parts[2]
            segment = parts[-1][-3:]
            short_name = name + "segment" + segment
            width, height = resolution.split("x")
        except Exception as e:
            print(f"❌ 跳过命名不规范文件：{file}")
            continue

        width, height, fps = int(width), int(height), int(fps)

        video_outdir = os.path.join(output_root, short_name)
        if os.path.exists(video_outdir):
            print(f"⏩ 已完成：{video_outdir}，跳过 {short_name}")
            continue
        stego_ipm_file = os.path.join(output_root2, short_name, f"{short_name}_stego_IPM.txt")
        os.makedirs(video_outdir, exist_ok=True)

        output_bitstream = os.path.join(video_outdir, f"{short_name}_stego.265")

        file_size = os.path.getsize(input_path)
        frame_size = int(width * height * 1.5)
        total_frames = int(file_size / frame_size)
        frame_num = 60  # 可自定义

        cmd = (
            f'"{x265_encoder}" '
            f'-p 5 --frame-threads 1 --rect '
            f'--input "{input_path}" '
            f'--input-res {width}x{height} '
            f'--fps {fps} '
            f'--output "{output_bitstream}" '
            f'--profile main '
            f'--frames {frame_num} '
            f'--keyint 4 --no-scenecut --b-adapt 0 --bframes 0 --qp {qp} '
            f'--InputStego="{stego_ipm_file}"'
        )

        print(f"🚀 开始处理：{file}")
        print(f"执行的命令：\n{cmd}")

        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='gbk'  # Windows 下部分 x265 编译版本输出是 gbk
            )

            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print(line, end='')

            process.wait()
            if process.returncode == 0:
                print(f"✅ 完成：{file}，输出在：{video_outdir}\n")
            else:
                print(f"❌ 编码失败：{file}，错误代码：{process.returncode}\n")
        except Exception as e:
            print(f"❌ 执行异常：{file}，错误信息：{str(e)}\n")
