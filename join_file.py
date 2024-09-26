import pandas as pd

# 读取两个CSV文件
df1 = pd.read_csv("scraped_scores.csv")
df2 = pd.read_csv("college_data.csv")

# 使用merge函数按照name列进行合并
merged_df = pd.merge(df1, df2, on="name", how="inner")

# 保存合并后的数据到新的CSV文件
merged_df.to_csv("merged_file.csv", index=False)

print("合并完成，结果已保存到 'merged_file.csv'")
