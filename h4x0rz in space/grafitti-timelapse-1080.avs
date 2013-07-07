LoadPlugin("deflicker.dll")

# TITLE

function FadeSubtitle(clip c, int start, int end, int fadeIn, int fadeOut, string text, int x, int y, int size)
{
	pre = BlankClip(c, length = start).KillAudio()
	title = BlankClip(c, length = (end - start)).KillAudio()
	title = Subtitle(title, text, font="Agency FB Fett", size=size, align=5, x=x, y=y, text_color=$00FFFFFF, halo_color=$FF000000)
	title = title.FadeIn(fadeIn).FadeOut(fadeOut)
	return Overlay(c, BlankClip(c, color=$FFFFFF), 0, 0, UnalignedSplice(pre, title))
}

shacklogo = ImageSource("shacklogo.png", end=289, fps=24).fadeIn(24)

title = BlankClip(length=280, width=1620, height=1080, fps=24).KillAudio()
title = Overlay(title, shacklogo, 588, 300)

title = FadeSubtitle(title, 73, 280, 12, 1, "@layer1gfx", 530, 550, 48)
title = FadeSubtitle(title, 80, 280, 12, 1, "@hdznrrd", 700, 550, 48)
title = FadeSubtitle(title, 87, 280, 12, 1, "@momorientes", 900, 550, 48)
title = FadeSubtitle(title, 94, 280, 12, 1, "@samuirai", 1100, 550, 48)

title = FadeSubtitle(title, 145, 224, 24, 7, "One Weekend", 810, 700, 48)
title = FadeSubtitle(title, 157, 224, 24, 7, "Twelve Square Meters Of Wall", 810, 750, 48)
title = FadeSubtitle(title, 169, 224, 24, 7, ">9000 Cans Of Spraypaint", 810, 800, 48)

challenge = ImageSource("determined-challenge-accepted copy.png", end=71, fps=24, pixel_type="RGB32").FadeIn(12)
challenge = BlankClip(challenge, length=217).KillAudio() + challenge
title = Overlay(title, challenge, 630, 580, challenge.ShowAlpha())

title = FadeSubtitle(title, 217, 280, 12, 1, "CHALLENGE", 430, 780, 120)
title = FadeSubtitle(title, 217, 280, 12, 1, "ACCEPTED", 1140, 780, 120)

title = FadeOut(title, 24) + BlankClip(title, length=9)

# MAIN PART

clip1 = ImageSource(file = "samstag abend/photos/IMG_%04d.JPG", start = 786, end = 1737, fps = 24).LanczosResize(1620,1080)
clip2 = ImageSource(file = "samstag abend/photos/IMG_%04d.JPG", start = 1738, end = 2210, fps = 24).LanczosResize(1620,1080)
clip3 = ImageSource(file = "sonntag/photos/IMG_%04d.JPG", start = 2211, end = 8131, fps = 24).LanczosResize(1620,1080)
still = ImageSource(file = "sonntag/photos/IMG_8131.JPG", end = 240, fps = 24).LanczosResize(1620,1080)
video = ConvertToYV12(UnalignedSplice(clip1, clip2, clip3, still)).Deflicker()

clock1 = ImageSource(file = "samstag abend/clocks/IMG_%04d.jpg.png", start = 786, end = 2210, fps = 24).Invert()
clock2 = ImageSource(file = "sonntag/clocks/IMG_%04d.jpg.png", start = 2211, end = 8131, fps = 24).Invert()
clockstill = ImageSource(file = "sonntag/clocks/IMG_8131.jpg.png", end = 56, fps = 24).Invert().FadeOut(56)
clock = UnalignedSplice(clock1, clock2, clockstill).AddBorders(50, 0, 50, 0)

dop3j0e = BlankClip(length=240, width=200, height=100, pixel_type="RGB24").KillAudio()
dop3j0e = Subtitle(dop3j0e, "@dop3j0e", font="Agency FB Fett", size=36, align=5, x=100, y=60, text_color=$00FFFFFF, halo_color=$FF000000)

overlay = Dissolve(clock, dop3j0e, 56)

video = Overlay(video, BlankClip(overlay, color = $FFFFFF), 1400, 930, overlay)

music = BlankClip(video, length=240 - 56).KillAudio()
music = Subtitle(music, "Music: '2012 Living Prophecy' by Tomas Phusion (CC-BY-NC)", font="Agency FB Fett", size=20, align=3, x=1610, y=1070, text_color=$00FFFFFF, halo_color=$FF000000)
music = BlankClip(video, length=clock.FrameCount).KillAudio() + FadeIn(music, 56)

video = Overlay(video, BlankClip(music, color = $FFFFFF), 0, 0, music)

#return BlankClip().Subtitle(String(title.Width) + String(title.Height) + String(video.Width) + String(video.Height))

ConvertToYV12(title) + video
#LanczosResize(1080, 720)
FadeOut2(120)
AddBorders(150, 0, 150, 0)

#Trim(0, 360)