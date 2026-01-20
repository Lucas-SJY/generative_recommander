from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="McAuley-Lab/Amazon-Reviews-2023",
    repo_type="dataset",
    allow_patterns=["raw/review_categories/*"],
    local_dir="./dataset",
    local_dir_use_symlinks=False,  # 确保是真实文件
)

print("Done. Files are in ./dataset/raw/review_categories/")