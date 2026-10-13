import os
from parse_ipm_coeff import (
    parse_ipm_multiframe,
    parse_transform_coeff_multiframe,
    build_ipm_map,
    build_coeff_map
)
from utils import save_ipm_and_coeff

# 视频分辨率（根据实际情况设置）
frame_width = 1920
frame_height = 1080
# segment_frame_count = 15

# 输出根目录
output_root = 'data_0.5_32'
cover_root = r'E:\xhy\Tar3Data\0.5_32\dec_ori_0.5_32'

# 所有视频（不再需要 start_frame_id）
video_names = [
    'aspen',
    'BasketballDrive',
    'BigBuckBunny',
    'BlueSky',
    'BQTerrace',
    'Cactus',
    'ControlledBurn',
    'CrowdRun',
    'dinner',
    'DucksTakeOff',
    'ElephantsDream',
    'factory',
    'InToTree',
    'Kimono1',
    'life',
    'OldTownCross',
    'ParkJoy',
    'ParkScene',
    'PedestrianArea',
    'RedKayak',
    'riverbed',
    'RushFieldCuts',
    'RushHour',
    'SintelTrailer2k',
    'SnowMnt',
    'SpeedBag',
    'station2',
    'sunflower',
    'TouchdownPass',
    'tractor',
    'WestWindEasy'
]

# 初始化帧号
global_frame_id = 1

for video_name in video_names:
    # 匹配所有 covers/<video_name>segmentXXX 目录
    segments = sorted([
        f for f in os.listdir(cover_root)
        if f.startswith(video_name)
    ])

    print(f"📦 Processing video: {video_name}, segments found: {len(segments)}")

    for segment in segments:
        seg_path = os.path.join(cover_root, segment)
        ipm_file = os.path.join(seg_path, f"{segment}_cover_ipm.txt")
        coeff_file = os.path.join(seg_path, f"{segment}_cover_coeff.txt")

        if not os.path.exists(ipm_file) or not os.path.exists(coeff_file):
            print(f"⚠️  Missing files in {segment}, skipping...")
            continue

        try:
            with open(ipm_file, 'r') as f:
                ipm_content = f.read()
            with open(coeff_file, 'r') as f:
                coeff_content = f.read()

            ipm_frames = parse_ipm_multiframe(ipm_content)
            # if len(ipm_frames) < segment_frame_count:
            #     print(f"⚠️  Segment {segment} has only {len(ipm_frames)} frames, skipping.")
            #     continue
            coeff_frames = parse_transform_coeff_multiframe(coeff_content)

            # 输出目录改为每个 segment 独立
            output_dir = os.path.join(output_root, segment)
            os.makedirs(output_dir, exist_ok=True)

            for i in ipm_frames:
                ipm_map = build_ipm_map(ipm_frames[i], frame_width, frame_height)
                coeff_map, block_map = build_coeff_map(coeff_frames.get(i, []), frame_width, frame_height)

                save_ipm_and_coeff(global_frame_id, ipm_map, coeff_map,block_map, output_dir)
                global_frame_id += 1

            print(f"✅ Finished segment {segment}")

        except Exception as e:
            print(f"❌ Error in segment {segment}: {e}")