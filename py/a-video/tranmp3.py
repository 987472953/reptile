import os
import subprocess


def process_video(input_path, output_path):
    # 构建ffmpeg命令
    ffmpeg_command = [
        "ffmpeg",
        "-f",
        "s16le",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-i", input_path,
        output_path,
        "-y"
    ]

    # 执行ffmpeg命令
    subprocess.run(ffmpeg_command)


def process_folder(input_folder, output_folder):
    # 遍历文件夹中的视频文件
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.pcm')):
                input_path = os.path.join(root, file)

                # 构建输出文件路径
                relative_path = os.path.relpath(input_path, input_folder)
                # pcm 换为 mp3
                output_path = os.path.join(output_folder, relative_path.replace(os.path.sep, os.path.sep)[:-3] + "mp3")

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
    # input_folder = '/Volumes/WD 500G/39.9尤克里里入门'
    input_folder = '/Users/mac/code/qufaya-image/vocalmusic_sound_Separation'
    output_folder = '/Users/mac/Downloads/vocalmusic_sound_Separation'

    process_folder(input_folder, output_folder)
