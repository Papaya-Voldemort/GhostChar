# Ghostchar App

> A quick note on AI: Some AI was used when building the desktop app. I have built with PyQt6 before but never put a icon on the top bar on MacOS so I used a little AI to figure that out. I also never found a good way to make a virtual camera with the app so I had some help integrating OBS virtual camera.

This is the Ghostchar App, its the coolest way to join ANY video call! Open it on MacOS and connect to any video call and boom your ASCII!

## The tech stack

For this app we used the following:
- Python
- PyQt6
- OBS Virtual Camera
- ONNX Runtime

and a few other peices not worth mentioning (I forgot...)

## Why only MacOS?

Right now only MacOS has a deployment. This is mostly because I don't use Windows enough to know how to add it seemlessly and building for windows would be quite hard... And linux is too varied for me to polish the app for it much.

Other OS builds might definity come in the future depending on how much traction this app gets but they are not confirmed.

## How to run?

Download the github release for easy usage...

Or if you really want to stress me out go ahead and build it yourself:
```
git clone https://github.com/Papaya-Voldemort/GhostChar.git
cd GhostChar
bash package_app.sh
```

That *should* work but let me know if it breaks...