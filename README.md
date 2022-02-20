<p align="center">
  <img src="/resource/favicon.png?raw=true" width="20%"></img>
</p>
[![Version](https://img.shields.io/badge/Version-v2022.02.20-green.svg)](https://github.com/hyugogirubato/AsyncFFmpegHelper/releases)


## Description
FFmpeg helper to download HLS streams faster in asynchronous mode.

## Features
- Download an HLS stream 7 times faster
- Resume download possible
- Support for ffmpeg arguments
- Choosing the location of the temporary folder
- Better audio stream selection than ffmpeg
- Best selection of video quality according to resolution
- Simplified video resolution extraction available


## List of arguments
| Argument            | Description                                  |
| :------------------ | :------------------------------------------- |
| `-h`, `--help`      | Show help menu                               |
| `-v`, `--version`   | Show script version                          |
| `-p`, `--path`      | Location of temporary files                  |
| `-i`, `--id`        | Process ID                                   |
| `-u`, `--url`       | Link of master m3u8 file                     |
| `-e`, `--extract`   | Get available video resolution               |
| `-d`, `--download`  | Download ID                                  |
| `-t`, `--tasks`     | Number of simultaneous downloads             |
| `-f`, `--ffmpeg`    | FFmpeg arguments                             |
| `-o`, `--output`    | Output file path                             |
| `-l`, `--log`       | Show process details                         |
| `-s`, `--skip`      | Do not download if the video already exists  |
| `-c`, `--clear`     | Clean up all temporary files                 | 


## Installation
````bash
pip install -r "requirements.txt"
````

## Use
<details><summary>Extract</summary>
Allows you to display the available video resolutions as well as the associated download ids.

````bash
main.py --id "PROCESS_ID" --url "URL" --extract
````

| Argument           | Type      | Description                                   |
| :----------------- | :-------- | :-------------------------------------------- |
| `-p`, `--path`     | `string`  | Location of temporary files                   |
| `-i`, `--id`       | `string`  | **Required**. Process ID                      |
| `-u`, `--url`      | `string`  | **Required**. Link of master m3u8 file        |
| `-e`, `--extract`  | `/`       | **Required**. Get available video resolution  |
| `-t`, `--tasks`    | `int`     | Number of simultaneous downloads              |
| `-l`, `--log`      | `/`       | Show process details                          |

</details>

<details><summary>Download</summary>
Download an HLS stream based on the id associated with the resolution.

````bash
main.py --id "PROCESS_ID" --url "URL" --download "ID" --tasks "TASKS" --ffmpeg="FFMPEG_ARGS" --output "OUTPUT" --skip
````

| Argument            | Type      | Description                                   |
| :------------------ | :-------- | :-------------------------------------------- |
| `-p`, `--path`      | `string`  | Location of temporary files                   |
| `-i`, `--id`        | `string`  | **Required**. Process ID                      |
| `-u`, `--url`       | `string`  | **Required**. Link of master m3u8 file        |
| `-e`, `--download`  | `int`     | **Required**. Get available video resolution  |
| `-t`, `--tasks`     | `int`     | Number of simultaneous downloads              |
| `-f`, `--ffmpeg`    | `string`  | FFmpeg arguments                              |
| `-o`, `--output`    | `string`  | **Required**. Output file path                |
| `-s`, `--skip`      | `/`       | Do not download if the video already exists   |
| `-l`, `--log`       | `/`       | Show process details                          |

NOTE: The ffmpeg arguments must not contain the input video stream and the location of the output file.
</details>

<details><summary>Clear</summary>
Delete the temporary directory and all the files it contains.

````bash
main.py --clear
````

| Argument         | Type      | Description                                 |
| :--------------- | :-------- | :------------------------------------------ |
| `-p`, `--path`   | `string`  | Location of temporary files                 |
| `-c`, `--clear`  | `/`       | **Required**. Clean up all temporary files  |

</details>

<details><summary>Version</summary>
Displays the script version.

````bash
main.py --version
````

| Argument           | Type  | Description                        |
| :----------------- | :---- | :--------------------------------- |
| `-v`, `--version`  | `/`   | **Required**. Show script version  |

</details>

---
*This script was created by the __Nashi Team__.  
Find us on [discord](https://discord.com/invite/g6JzYbh) for more information on projects in development.*
