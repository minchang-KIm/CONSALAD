import os
from PIL import Image
from PIL import ImageFilter
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFile
import urllib.request
import json
from mutagen.mp3 import MP3
import math
import makeAss_mubeat
import re
import ssl
ImageFile.LOAD_TRUNCATED_IMAGES = True

def resolution(number):
    resolution = 1.5
    return int(number * resolution)

def makeAssAndImages(PATH, lyricApi, seq, artist, trackName):
    with urllib.request.urlopen(lyricApi, context=ssl._create_unverified_context()) as url:


        data = json.loads(url.read().decode())
        if len(data['lyrics']) is 1:

            baseSize = (resolution(1280), resolution(720))
            gaussianBlur = ImageFilter.GaussianBlur(resolution(25))

            # 음악 불러온 후 초 계산
            audio = MP3(PATH + seq + "/track.mp3")
            timeValue = math.ceil(audio.info.length)

            cover = Image.open(PATH + seq + "/cover.jpg").convert('RGBA')
            cover_mask = Image.open(os.path.join(os.path.dirname(__file__), 'img/cover_mask.png')).convert(
                'RGBA').resize((resolution(340), resolution(340)))
            background = Image.new("RGBA", (resolution(1500), resolution(1500)))
            cover_background = Image.blend(cover.resize((resolution(1500), resolution(1500))).filter(gaussianBlur), background, 0.33)

            result = Image.new("RGB", baseSize)
            result.paste(cover_background, imgSizeCalc(resolution(-110), resolution(-390), resolution(1500), resolution(1500)))
            result.paste(cover.resize((resolution(340), resolution(340))), imgSizeCalc(resolution(470), resolution(97), resolution(340), resolution(340)), mask=cover_mask.split()[3])


            if len(trackName) > 50:
                if len(re.findall(r'[\u4e00-\u9fff]+', trackName)) >= 1:
                    font_title = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(15))
                else:
                    font_title = ImageFont.truetype("NanumSquareEB.ttf", resolution(15))
            elif len(trackName) > 35:
                if len(re.findall(r'[\u4e00-\u9fff]+', trackName)) >= 1:
                    font_title = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(20))
                else:
                    font_title = ImageFont.truetype("NanumSquareEB.ttf", resolution(20))
            else:
                if len(re.findall(r'[\u4e00-\u9fff]+', trackName)) >= 1:
                    font_title = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(30))
                else:
                    font_title = ImageFont.truetype("NanumSquareEB.ttf", resolution(30))

            if len(re.findall(r'[\u4e00-\u9fff]+', artist)) >= 1:
                font_artist = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(20)) if len(artist) < 50 else ImageFont.truetype(
                "NotoSansCJK-Bold.ttc", resolution(15))
            else:
                font_artist = ImageFont.truetype("NanumSquareB.ttf", resolution(20)) if len(artist) < 50 else ImageFont.truetype(
                "NanumSquareB.ttf", resolution(15))

            font_time = ImageFont.truetype("NanumSquareEB.ttf", resolution(20))

            shareTxt = Image.new("RGBA", baseSize, (255, 255, 255, 0))
            share_Text_draw = ImageDraw.Draw(shareTxt)

            # 트랙명, 아티스트 영역 사이즈
            titleW, titleH = (resolution(640), resolution(42))
            titleText = trackName
            w, h = font_title.getsize((titleText))

            share_Text_draw.text((titleW - w / 2, resolution(465)), titleText, (255, 255, 255), font=font_title)

            artistW, artistH = (resolution(640), resolution(42.5))
            artistText = artist
            w, h = font_artist.getsize((artistText))
            share_Text_draw.text((artistW - w / 2, resolution(515)), artistText, (255, 255, 255, 102), font=font_artist)

            createFloder(PATH + seq + "/result/")
            for imgIndex in range(timeValue + 1):

                txt = Image.new("RGBA", baseSize, (255, 255, 255, 0))
                text_draw = ImageDraw.Draw(txt)

                startTimeW, startTimeH = (resolution(395), resolution(597))
                startTimeText = str(imgIndex // 60) + ":" + (
                    ("0" + str(imgIndex % 60)) if (imgIndex % 60 < 10) else str(imgIndex % 60))
                w, h = font_time.getsize((startTimeText))
                text_draw.text((startTimeW, startTimeH), startTimeText, (255, 255, 255, 162), font=font_time)

                endTimeW, endTimeH = (resolution(839), resolution(595))
                endTimeValie = timeValue - imgIndex
                endTimeText = str(endTimeValie // 60) + ":" + (
                    ("0" + str(endTimeValie % 60)) if (endTimeValie % 60 < 10) else str(endTimeValie % 60))
                w, h = font_time.getsize((endTimeText))
                text_draw.text((endTimeW, endTimeH), endTimeText, (255, 255, 255, 162), font=font_time)

                timeBarArea = Image.new("RGBA", baseSize, (255, 255, 255, 0))
                timeBar_draw = ImageDraw.Draw(timeBarArea)
                rounded_rectangle(timeBar_draw, rounded_rectangleSizeCalc(resolution(397), resolution(580), resolution(485), resolution(8)), resolution(4), fill=(255, 255, 255, 30))

                corner_radius = imgIndex if imgIndex < resolution(4) else resolution(4)
                rounded_rectangle(timeBar_draw, rounded_rectangleSizeCalc(resolution(397), resolution(580), (resolution(485) / timeValue * imgIndex), resolution(8)),
                                  corner_radius, fill=(255, 255, 255, 255))

                out = Image.alpha_composite(result.convert('RGBA'), shareTxt)
                out = Image.alpha_composite(out, txt)
                out2 = Image.alpha_composite(out, timeBarArea)

                fileIndex = str(imgIndex)
                if imgIndex > 99:
                    fileIndex = "0" + fileIndex
                elif imgIndex > 9:
                    fileIndex = "00" + fileIndex
                elif imgIndex <= 9:
                    fileIndex = "000" + fileIndex

                out2.save(PATH + seq + "/result/" + fileIndex + ".png")

            os.chdir(PATH + seq + "/result")
            os.system("ffmpeg -threads 1 -framerate 1 -i %4d.png -c:v libx264 -r 15 -pix_fmt yuv420p -preset ultrafast -crf 25 -y ../output.mp4")


        else:
            f = open(PATH + seq + "/lyric.ass", 'w', encoding='utf8')
            f.write(makeAss_mubeat.makeAss(data))
            f.close()

            baseSize = (resolution(1280), resolution(720))
            gaussianBlur = ImageFilter.GaussianBlur(resolution(25))

            # 음악 불러온 후 초 계산
            audio = MP3(PATH + seq + "/track.mp3")
            timeValue = math.ceil(audio.info.length)

            cover = Image.open(PATH + seq + "/cover.jpg").convert('RGBA')
            cover_mask = Image.open(os.path.join(os.path.dirname(__file__), 'img/cover_mask.png')).convert('RGBA').resize((resolution(340), resolution(340)))
            background = Image.new("RGBA", (resolution(1500), resolution(1500)))
            cover_background = Image.blend(cover.resize((resolution(1500), resolution(1500))).filter(gaussianBlur), background, 0.33)

            result = Image.new("RGB", baseSize)
            result.paste(cover_background, imgSizeCalc(resolution(-110), resolution(-390), resolution(1500), resolution(1500)))
            result.paste(cover.resize((resolution(340), resolution(340))), imgSizeCalc(resolution(163), resolution(97), resolution(340), resolution(340)), mask=cover_mask.split()[3])


            if len(trackName) > 50:
                if len(re.findall(r'[\u4e00-\u9fff]+', trackName)) >= 1:
                    font_title = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(15))
                else:
                    font_title = ImageFont.truetype("NanumSquareEB.ttf", resolution(15))
            elif len(trackName) > 35:
                if len(re.findall(r'[\u4e00-\u9fff]+', trackName)) >= 1:
                    font_title = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(20))
                else:
                    font_title = ImageFont.truetype("NanumSquareEB.ttf", resolution(20))
            else:
                if len(re.findall(r'[\u4e00-\u9fff]+', trackName)) >= 1:
                    font_title = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(30))
                else:
                    font_title = ImageFont.truetype("NanumSquareEB.ttf", resolution(30))

            if len(re.findall(r'[\u4e00-\u9fff]+', artist)) >= 1:
                font_artist = ImageFont.truetype("NotoSansCJK-Bold.ttc", resolution(20)) if len(artist) < 50 else ImageFont.truetype(
                "NotoSansCJK-Bold.ttc", resolution(15))
            else:
                font_artist = ImageFont.truetype("NanumSquareB.ttf", resolution(20)) if len(artist) < 50 else ImageFont.truetype(
                "NanumSquareB.ttf", resolution(15))

            font_time = ImageFont.truetype("NanumSquareEB.ttf", resolution(20))

            shareTxt = Image.new("RGBA", baseSize, (255, 255, 255, 0))
            share_Text_draw = ImageDraw.Draw(shareTxt)

            # 트랙명, 아티스트 영역 사이즈
            titleW, titleH = (resolution(335), resolution(42))
            titleText = trackName
            w, h = font_title.getsize((titleText))

            share_Text_draw.text((titleW - w / 2, resolution(465)), titleText, (255, 255, 255), font=font_title)

            artistW, artistH = (resolution(335), resolution(42.5))
            artistText = artist
            w, h = font_artist.getsize((artistText))
            share_Text_draw.text((artistW - w / 2, resolution(515)), artistText, (255, 255, 255, 102), font=font_artist)

            createFloder(PATH + seq + "/result/")
            for imgIndex in range(timeValue + 1):

                txt = Image.new("RGBA", baseSize, (255, 255, 255, 0))
                text_draw = ImageDraw.Draw(txt)

                startTimeW, startTimeH = (resolution(86), resolution(597))
                startTimeText = str(imgIndex // 60) + ":" + (
                    ("0" + str(imgIndex % 60)) if (imgIndex % 60 < 10) else str(imgIndex % 60))
                w, h = font_time.getsize((startTimeText))
                text_draw.text((startTimeW, startTimeH), startTimeText, (255, 255, 255, 162), font=font_time)

                endTimeW, endTimeH = (resolution(530), resolution(595))
                endTimeValie = timeValue - imgIndex
                endTimeText = str(endTimeValie // 60) + ":" + (
                    ("0" + str(endTimeValie % 60)) if (endTimeValie % 60 < 10) else str(endTimeValie % 60))
                w, h = font_time.getsize((endTimeText))
                text_draw.text((endTimeW, endTimeH), endTimeText, (255, 255, 255, 162), font=font_time)

                timeBarArea = Image.new("RGBA", baseSize, (255, 255, 255, 0))
                timeBar_draw = ImageDraw.Draw(timeBarArea)
                rounded_rectangle(timeBar_draw, rounded_rectangleSizeCalc(resolution(88), resolution(580), resolution(485), resolution(8)), resolution(4), fill=(255, 255, 255, 30))

                corner_radius = imgIndex if imgIndex < 4 else 4
                rounded_rectangle(timeBar_draw, rounded_rectangleSizeCalc(resolution(88), resolution(580), (resolution(485) / timeValue * imgIndex), resolution(8)),
                                  corner_radius, fill=(255, 255, 255, 255))

                out = Image.alpha_composite(result.convert('RGBA'), shareTxt)
                out = Image.alpha_composite(out, txt)
                out2 = Image.alpha_composite(out, timeBarArea)

                fileIndex = str(imgIndex)
                if imgIndex > 99:
                    fileIndex = "0" + fileIndex
                elif imgIndex > 9:
                    fileIndex = "00" + fileIndex
                elif imgIndex <= 9:
                    fileIndex = "000" + fileIndex

                out2.save(PATH + seq + "/result/" + fileIndex + ".png")

            os.chdir(PATH + seq + "/result/")
            os.system("ffmpeg -threads 1 -framerate 1 -i %4d.png -c:v libx264 -r 15 -pix_fmt yuv420p -preset ultrafast -crf 25 -y ../output.mp4")


def imgSizeCalc(x, y, width, height):
    return (x, y, width + x, height + y)


def rounded_rectangleSizeCalc(x, y, width, height):
    return ((x, y), (width + x, height + y))


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def rounded_rectangle(self: ImageDraw, xy, corner_radius, fill=None, outline=None):
    upper_left_point = xy[0]
    bottom_right_point = xy[1]
    self.rectangle(
        [
            (upper_left_point[0], upper_left_point[1] + corner_radius),
            (bottom_right_point[0], bottom_right_point[1] - corner_radius)
        ],
        fill=fill,
        outline=outline
    )
    self.rectangle(
        [
            (upper_left_point[0] + corner_radius, upper_left_point[1]),
            (bottom_right_point[0] - corner_radius, bottom_right_point[1])
        ],
        fill=fill,
        outline=outline
    )
    self.pieslice([upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
        180,
        270,
        fill=fill,
        outline=outline
    )
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
        0,
        90,
        fill=fill,
        outline=outline
    )
    self.pieslice([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2), (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
        90,
        180,
        fill=fill,
        outline=outline
    )
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]), (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
        270,
        360,
        fill=fill,
        outline=outline
    )


def createFloder(dic):
    try:
        if not os.path.exists(dic):
            os.makedirs(dic)
    except OSError:
        print("error")