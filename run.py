# batch_extractRDcost.py->
# batch_buildDDG.py->
# build_embedplan.py->
# batch_embed_stc_ipm.py->Cencoder.py->StegoDecoder.py
# import subprocess
# process1 = subprocess.Popen(['python', 'decodeorg.py'])
# # 启动第二个脚本
# process2 = subprocess.Popen(['python', 'decodesteg.py'])
# #
# # # 等待两个进程都完成
# process1.wait()
# process2.wait()
# # process6=subprocess.Popen(['python','generate_pu_mask.py'])
# process3=subprocess.Popen(['python', 'generate_map.py'])
# process4=subprocess.Popen(['python', 'generate_stego_map.py'])
# # 等待两个进程都完成
# process3.wait()
# process4.wait()
# # process6.wait()
#
import subprocess

subprocess.run(['python', 'batch_extractRDcost.py'], check=True)
#
subprocess.run(['python', 'batch_buildDDG.py'], check=True)
subprocess.run(['python', 'build_embedplan.py'], check=True)
# subprocess.run(['python', 'batch_embed_stc_ipm.py'], check=True)
# subprocess.run(['python', 'Cencoder.py'], check=True)
# subprocess.run(['python', 'StegoDecoder.py'], check=True)
# subprocess.run(['python', 'batch_embed_stc_ipm.py'], check=True)
# process1=subprocess.Popen(['python', 'Cencoder.py'])
# process2=subprocess.Popen(['python', 'Cencoder2.py'])
subprocess.run(['python', 'batch_embed_stc_ipm.py'], check=True)
process3=subprocess.Popen(['python', 'Cencoder3.py'])
process1=subprocess.Popen(['python', 'Cencoder.py'])
process2=subprocess.Popen(['python', 'Cencoder2.py'])
process1.wait()
process2.wait()
process3.wait()
process6=subprocess.Popen(['python', 'StegoDecoder3.py'])
process4=subprocess.Popen(['python', 'StegoDecoder.py'])
process5=subprocess.Popen(['python', 'StegoDecoder2.py'])
process6.wait()
process4.wait()
process5.wait()
# subprocess.run(['python', 'StegoDecoder3.py'], check=True)
# subprocess.run(['python', 'StegoDecoder2.py'], check=True)
#
# subprocess.run(['python', 'StegoDecoder.py'], check=True)