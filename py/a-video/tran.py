import os
import subprocess


def process_video(input_path, output_path):
    logo_path = "/Users/mac/Downloads/logo.png"  # 你的logo文件路径

    # 构建ffmpeg命令
    ffmpeg_command = [
        "ffmpeg",
        "-i", input_path,
        "-i", logo_path,
        "-filter_complex", "[1:v]scale=iw*2:ih*2[wm];[0:v][wm]overlay=W-w-80:h-80",
        "-vcodec", "libx264",
        "-crf", "35",
        "-preset", "fast",
        "-codec:a", "aac",
        "-b:a", "96k",
        output_path,
        "-y"
    ]

    # 执行ffmpeg命令
    subprocess.run(ffmpeg_command)


def process_folder(input_folder, output_folder):
    # 遍历文件夹中的视频文件
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                input_path = os.path.join(root, file)

                # 构建输出文件路径
                relative_path = os.path.relpath(input_path, input_folder)
                output_path = os.path.join(output_folder, relative_path.replace(os.path.sep, os.path.sep))

                # 创建输出文件夹
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                print(input_path)
                print(output_path)

                if os.path.exists(output_path):
                    print("已存在" + output_path)
                    continue

                print("________")

                # 处理视频
                try:
                    process_video(input_path, output_path)
                except Exception as e:
                    print(e)
                    os.remove(output_path)


if __name__ == "__main__":
    input_folder = '/Volumes/WD 500G/39.9尤克里里入门'
    output_folder = '/Users/mac/Downloads/39.9尤克里里入门'

    process_folder(input_folder, output_folder)
