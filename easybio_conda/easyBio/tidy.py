
# from .Utils import tidySummary
# import os
# import shutil


# matricespath = "/home/data/user/lei/SRAData/GSE/GSE162454/raw//matrices"
# outputpath = "/home/data/user/lei/SRAData/GSE/GSE162454/raw//output"


# def tidySummary(matrices_base, output_base):
#     summary_base = os.path.join(output_base, "summary")
#     matrix_base = os.path.join(output_base, "matrix")
#     matrixh5_base = os.path.join(output_base, "matrixh5")
#     loomFile_base = os.path.join(output_base, "loomfile")

#     # 如果目标文件夹不存在，创建它
#     os.makedirs(summary_base, exist_ok=True)
#     os.makedirs(matrix_base, exist_ok=True)
#     os.makedirs(matrixh5_base, exist_ok=True)
#     os.makedirs(loomFile_base, exist_ok=True)

#     for folder in os.listdir(matrices_base):
#         src_folder = os.path.join(matrices_base, folder)

#         if os.path.isdir(src_folder):
#             src_file = os.path.join(src_folder, 'outs', 'web_summary.html')
#             src_matrix_folder = os.path.join(
#                 src_folder, 'outs', 'filtered_feature_bc_matrix')
#             matrixh5flie = os.path.join(
#                 src_folder, 'outs', 'filtered_feature_bc_matrix.h5')
#             loom_file = os.path.join(
#                 src_folder, 'velocyto', f'{folder}.loom')

#             if os.path.exists(src_file):
#                 dst_file = os.path.join(summary_base, folder + '.html')
#                 if not os.path.exists(dst_file):
#                     shutil.copy2(src_file, dst_file)
                
#             if os.path.exists(src_matrix_folder):
#                 dst_matrix_folder = os.path.join(matrix_base, folder)
#                 if not os.path.exists(dst_matrix_folder):
#                     shutil.copytree(src_matrix_folder, dst_matrix_folder)
            
#             if os.path.exists(matrixh5flie):
#                 dst_matrixh5_folder = os.path.join(matrixh5_base, folder)
#                 if not os.path.exists(dst_matrixh5_folder):
#                     shutil.copy2(matrixh5flie, dst_matrixh5_folder)
                    
#             if os.path.exists(matrixh5flie):
#                 loomFile_base_folder = os.path.join(loomFile_base, folder)
#                 if not os.path.exists(loomFile_base_folder):
#                     shutil.copy2(loom_file, loomFile_base_folder)
                    
                    
# tidySummary(matricespath, outputpath)

# outputpath = f"/home/data/groupdata/杨骁老师原始数据/output"
# os.makedirs(outputpath, exist_ok=True)
#        # 设置源文件夹和目标文件夹的路径
# tidySummary("/home/data/groupdata/杨骁老师原始数据/matrices", outputpath)
