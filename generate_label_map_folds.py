# import os
# import json
# import random
# import re
# from collections import defaultdict
#
# data_root = './data_0.3_28'
# videos = [
#     'aspen', 'BasketballDrive', 'BigBuckBunny', 'BlueSky', 'BQTerrace', 'Cactus',
#     'ControlledBurn', 'CrowdRun', 'dinner', 'DucksTakeOff', 'ElephantsDream', 'factory',
#     'InToTree', 'Kimono1', 'life', 'OldTownCross', 'ParkJoy', 'ParkScene', 'PedestrianArea',
#     'RedKayak', 'riverbed', 'RushFieldCuts', 'RushHour', 'SintelTrailer2k', 'SnowMnt',
#     'SpeedBag', 'station2', 'sunflower', 'TouchdownPass', 'tractor', 'WestWindEasy'
# ]
#
# def extract_frame_id(filename):
#     match = re.search(r'frame_(\d+)', filename)
#     return match.group(1) if match else None
#
# # 创建20次不同的随机拆分
# for split_id in range(1, 2):
#     random.seed(split_id)
#
#     train_label_map = {}
#     test_label_map = {}
#
#     for video in videos:
#         cover_frames = []
#         stego_frames = []
#
#         for segment_folder in os.listdir(data_root):
#             if not segment_folder.lower().startswith(video.lower()):
#                 continue
#             segment_path = os.path.join(data_root, segment_folder)
#             if not os.path.isdir(segment_path):
#                 continue
#
#             for fname in os.listdir(segment_path):
#                 frame_id = extract_frame_id(fname)
#                 if frame_id:
#                     if 'stego' in fname:
#                         stego_frames.append(frame_id)
#                     else:
#                         cover_frames.append(frame_id)
#
#         cover_frames = sorted(list(set(cover_frames)))
#         stego_frames = sorted(list(set(stego_frames)))
#
#         train_cover_count = int(len(cover_frames) * 0.8)
#         train_stego_count = int(len(stego_frames) * 0.8)
#
#         random.shuffle(cover_frames)
#         train_cover_frames = cover_frames[:train_cover_count]
#         test_cover_frames = cover_frames[train_cover_count:]
#
#         random.shuffle(stego_frames)
#         train_stego_frames = stego_frames[:train_stego_count]
#         test_stego_frames = stego_frames[train_stego_count:]
#
#         for frame_id in train_cover_frames:
#             train_label_map[frame_id] = 0
#         for frame_id in train_stego_frames:
#             train_label_map[frame_id + '_stego'] = 1
#
#         for frame_id in test_cover_frames:
#             test_label_map[frame_id] = 0
#         for frame_id in test_stego_frames:
#             test_label_map[frame_id + '_stego'] = 1
#
#     # === 新增：从 train_label_map 中生成 val_label_map，视频级别划分 ===
#     def get_video_id(frame_id):
#         base_id = frame_id.replace('_stego', '')
#         return base_id.split('_')[0]
#
#     video_to_frames = defaultdict(list)
#     for frame_id in train_label_map:
#         video_id = get_video_id(frame_id)
#         video_to_frames[video_id].append(frame_id)
#
#     video_ids = list(video_to_frames.keys())
#     random.shuffle(video_ids)
#     val_video_count = max(1, int(len(video_ids) * 0.1))
#     val_videos = set(video_ids[:val_video_count])
#
#     val_label_map = {}
#     new_train_label_map = {}
#
#     for video_id, frame_list in video_to_frames.items():
#         if video_id in val_videos:
#             for fid in frame_list:
#                 val_label_map[fid] = train_label_map[fid]
#         else:
#             for fid in frame_list:
#                 new_train_label_map[fid] = train_label_map[fid]
#
#     output_dir = 'splits_0.3_28'
#     os.makedirs(output_dir, exist_ok=True)
#
#     with open(os.path.join(output_dir, f'label_map_train_split{split_id}.json'), 'w') as f:
#         json.dump(new_train_label_map, f)
#     with open(os.path.join(output_dir, f'label_map_test_split{split_id}.json'), 'w') as f:
#         json.dump(test_label_map, f)
#     with open(os.path.join(output_dir, f'label_map_val_split{split_id}.json'), 'w') as f:
#         json.dump(val_label_map, f)
#
#     train_cover = sum(1 for v in new_train_label_map.values() if v == 0)
#     train_stego = sum(1 for v in new_train_label_map.values() if v == 1)
#     val_cover = sum(1 for v in val_label_map.values() if v == 0)
#     val_stego = sum(1 for v in val_label_map.values() if v == 1)
#     test_cover = sum(1 for v in test_label_map.values() if v == 0)
#     test_stego = sum(1 for v in test_label_map.values() if v == 1)
#
#     print(f"Split{split_id}: Train - Cover: {train_cover}, Stego: {train_stego} | "
#           f"Val - Cover: {val_cover}, Stego: {val_stego} | "
#           f"Test - Cover: {test_cover}, Stego: {test_stego}")
#     print(f"Split{split_id} label maps generated.\n")
#
# print("All 20 splits generated successfully.")
import os
import json
import random
import re
from collections import defaultdict

data_root = './data_0.5_32'
videos = [
    'aspen', 'BasketballDrive', 'BigBuckBunny', 'BlueSky', 'BQTerrace', 'Cactus',
    'ControlledBurn', 'CrowdRun', 'dinner', 'DucksTakeOff', 'ElephantsDream', 'factory',
    'InToTree', 'Kimono1', 'life', 'OldTownCross', 'ParkJoy', 'ParkScene', 'PedestrianArea',
    'RedKayak', 'riverbed', 'RushFieldCuts', 'RushHour', 'SintelTrailer2k', 'SnowMnt',
    'SpeedBag', 'station2', 'sunflower', 'TouchdownPass', 'tractor', 'WestWindEasy'
]

def extract_frame_id(filename, segment_folder):
    """返回全局唯一帧ID: segmentName_frameID"""
    match = re.search(r'frame_(\d+)', filename)
    return f"{segment_folder}_frame_{match.group(1)}" if match else None

# 创建拆分
for split_id in range(1, 2):
    random.seed(split_id)

    train_label_map = {}
    test_label_map = {}

    for video in videos:
        cover_frames = []
        stego_frames = []

        for segment_folder in os.listdir(data_root):
            if not segment_folder.lower().startswith(video.lower()):
                continue
            segment_path = os.path.join(data_root, segment_folder)
            if not os.path.isdir(segment_path):
                continue

            for fname in os.listdir(segment_path):
                frame_id = extract_frame_id(fname, segment_folder)
                if frame_id:
                    if 'stego' in fname:
                        stego_frames.append(frame_id)
                    else:
                        cover_frames.append(frame_id)

        cover_frames = sorted(list(set(cover_frames)))
        stego_frames = sorted(list(set(stego_frames)))

        train_cover_count = int(len(cover_frames) * 0.8)
        train_stego_count = int(len(stego_frames) * 0.8)

        random.shuffle(cover_frames)
        train_cover_frames = cover_frames[:train_cover_count]
        test_cover_frames = cover_frames[train_cover_count:]

        random.shuffle(stego_frames)
        train_stego_frames = stego_frames[:train_stego_count]
        test_stego_frames = stego_frames[train_stego_count:]

        for frame_id in train_cover_frames:
            train_label_map[frame_id] = 0
        for frame_id in train_stego_frames:
            train_label_map[frame_id + '_stego'] = 1

        for frame_id in test_cover_frames:
            test_label_map[frame_id] = 0
        for frame_id in test_stego_frames:
            test_label_map[frame_id + '_stego'] = 1

    # === 基于 segment_name 抽验证集 ===
    def get_segment_id(frame_id):
        return frame_id.split('_frame_')[0]  # 取 segmentName

    segment_to_frames = defaultdict(list)
    for frame_id in train_label_map:
        segment_id = get_segment_id(frame_id)
        segment_to_frames[segment_id].append(frame_id)

    segment_ids = list(segment_to_frames.keys())
    random.shuffle(segment_ids)
    val_segment_count = max(1, int(len(segment_ids) * 0.1))
    val_segments = set(segment_ids[:val_segment_count])

    val_label_map = {}
    new_train_label_map = {}

    for segment_id, frame_list in segment_to_frames.items():
        if segment_id in val_segments:
            for fid in frame_list:
                val_label_map[fid] = train_label_map[fid]
        else:
            for fid in frame_list:
                new_train_label_map[fid] = train_label_map[fid]

    # === 输出 ===
    output_dir = 'splits_0.5_32'
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, f'label_map_train_split{split_id}.json'), 'w') as f:
        json.dump(new_train_label_map, f)
    with open(os.path.join(output_dir, f'label_map_test_split{split_id}.json'), 'w') as f:
        json.dump(test_label_map, f)
    with open(os.path.join(output_dir, f'label_map_val_split{split_id}.json'), 'w') as f:
        json.dump(val_label_map, f)

    # === 统计 ===
    train_cover = sum(1 for v in new_train_label_map.values() if v == 0)
    train_stego = sum(1 for v in new_train_label_map.values() if v == 1)
    val_cover = sum(1 for v in val_label_map.values() if v == 0)
    val_stego = sum(1 for v in val_label_map.values() if v == 1)
    test_cover = sum(1 for v in test_label_map.values() if v == 0)
    test_stego = sum(1 for v in test_label_map.values() if v == 1)

    print(f"Split{split_id}: Train - Cover: {train_cover}, Stego: {train_stego} | "
          f"Val - Cover: {val_cover}, Stego: {val_stego} | "
          f"Test - Cover: {test_cover}, Stego: {test_stego}")

    # === 检查集合是否有交集 ===
    overlap = (set(new_train_label_map) & set(val_label_map)) | \
              (set(new_train_label_map) & set(test_label_map)) | \
              (set(val_label_map) & set(test_label_map))
    print(f"Overlap count: {len(overlap)}")
    print(f"Split{split_id} label maps generated.\n")

print("Segment-based splits generated successfully.")
