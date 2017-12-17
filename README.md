### 训练
1. 原始训练语料拷贝到工程目录下，文件名`emoji_sample.txt`  
2. 清洗并生成训练数据，并执行训练  
`python3 emoji_lm.py --data_path=./data/ --clean_data=True`  
或者离线执行  
`nohup python3 -u emoji_lm.py --data_path=./data/ --clean_data=True &  `


### 评估
1. 准备测试数据xxx  
2. 执行评估过程  
`python3 emoji_lm.py --test_path=xxx --predict=True`  
或者离线执行  
`nohup python3 -u emoji_lm.py --test_path=xxx --predict=True &  `  
