import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def parse_ipm_file(file_path):
    frames = defaultdict(dict)
    current_frame = -1
    with open(file_path, 'r') as f:
        for line in f:
            if "Frame" in line and "begin" in line:
                current_frame = int(re.search(r'Frame (\d+)', line).group(1))
            elif "Frame" in line and "end" in line:
                current_frame = -1
            elif current_frame != -1:
                match = re.search(r'x=(\d+),y=(\d+).*IPM=(\d+)', line)
                if match:
                    x, y, ipm = map(int, match.groups())
                    frames[current_frame][(x, y)] = ipm
    return frames

def generate_change_map(cover_frame, steg_frame, width, height, block_size=4):
    mask = np.zeros((height, width), dtype=np.uint8)
    for (x, y), ipm_cover in cover_frame.items():
        ipm_steg = steg_frame.get((x, y), ipm_cover)
        if ipm_cover != ipm_steg:
            mask[y:y+block_size, x:x+block_size] = 255
    return mask

def visualize_and_save(mask, frame_index, out_dir):
    plt.figure(figsize=(10, 6))
    plt.imshow(mask, cmap='gray')
    plt.title(f'IPM Change Map - Frame {frame_index}')
    plt.axis('off')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'frame_{frame_index:04d}.png')
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()

def main(cover_path, steg_path, out_dir='1_8_change_maps', resolution=(1920, 1080)):
    width, height = resolution
    cover_data = parse_ipm_file(cover_path)
    steg_data = parse_ipm_file(steg_path)

    for frame_idx in sorted(cover_data.keys()):
        cover_frame = cover_data[frame_idx]
        steg_frame = steg_data.get(frame_idx, {})
        mask = generate_change_map(cover_frame, steg_frame, width, height)
        visualize_and_save(mask, frame_idx, out_dir)
        print(f'Frame {frame_idx} processed.')

# === 使用示例 ===
if __name__ == "__main__":
    cover_file = r'E:\xhy\Tar3Data\0.5_24\dec_ori_0.5_24\aspensegment000\aspensegment000_cover_ipm.txt'
    #cover_file = r'E:\xhy\Tar5Stego\results\dec_0.3_32_steg\aspensegment000\aspensegment000_steg_ipm.txt'

    # E:\xhy\Tar5Stego\results\dec_0.3_32_steg\aspensegEment000
    steg_file  = r'E:\xhy\Tar5Stego\results\dec_steg_0.1_24\aspensegment000\aspensegment000_steg_ipm.txt'
    main(cover_file, steg_file, out_dir='0.1_24_change_maps_aspensegment000_new', resolution=(1920, 1080))
