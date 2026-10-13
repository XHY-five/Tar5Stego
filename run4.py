import subprocess

process3=subprocess.Popen(['python', 'generate_map.py'])
process4=subprocess.Popen(['python', 'generate_stego_map.py'])
# # 等待两个进程都完成
process3.wait()
process4.wait()
# # process6.wait()
#
subprocess.run(['python', 'generate_label_map_folds.py'], check=True)