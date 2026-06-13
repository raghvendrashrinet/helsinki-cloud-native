##  yt-dlp command line vedio downloader supports multiple eg youtube,imgur etc
 yt-dlp is a program that downloads YouTube and Imgur videos
### Docker File
```
FROM ubuntu:24.04

WORKDIR /mydir

#DEBIAN_FRONTEND environment variable to noninteractive,This tells apt to automatically accept default values (usually UTC) instead of asking for your geographic area
RUN export DEBIAN_FRONTEND=noninteractive &&     apt-get update &&     apt-get install -y curl python3 ffmpeg

# Downloading yt-dlp package in /usr/local/bin/ folder for executable path
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp

# Change permission
RUN chmod +x yt-dlp

ENTRYPOINT ["/usr/local/bin/yt-dlp"]

# define a default argument
CMD ["https://www.youtube.com/watch?v=Aa55RKWZxxI"]

#now build and run as below
#$ docker build -t yt-dlp .
#$ docker run yt-dlp https://www.youtube.com/watch?v=uTZSILGTskA



```

### provide youtube link while creating the container
> #$ docker run yt-dlp https://www.youtube.com/watch?v=uTZSILGTskA
