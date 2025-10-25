import os
import argparse
from huggingface_hub import snapshot_download
import sys


def main():
    parser = argparse.ArgumentParser(description="下载HuggingFace模型")
    parser.add_argument(
        "--model-name",
        default="Qwen/Qwen2-0.5B-Instruct",
        help="模型名称，例如: Qwen/Qwen2-0.5B-Instruct",
    )
    parser.add_argument("--output-dir", default="./models", help="模型保存目录")
    parser.add_argument("--local-dir", help="本地目录名，默认使用模型名称")

    args = parser.parse_args()

    # 设置本地目录
    if args.local_dir is None:
        # 从模型名称提取目录名
        model_dir_name = args.model_name.split("/")[-1]
        local_dir = os.path.join(args.output_dir, model_dir_name)
    else:
        local_dir = os.path.join(args.output_dir, args.local_dir)

    print(f"开始下载模型: {args.model_name}")
    print(f"保存到: {local_dir}")

    try:
        # 创建输出目录
        os.makedirs(args.output_dir, exist_ok=True)

        # 下载模型
        snapshot_download(
            repo_id=args.model_name,
            local_dir=local_dir,
            local_dir_use_symlinks=False,  # 不使用符号链接，直接复制文件
            resume_download=True,  # 支持断点续传
        )

        print(f"✅ 模型下载完成: {local_dir}")

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
